"""One client for OpenAI, Groq and Ollama (all speak the OpenAI chat-completions protocol).

* Every call is cached on disk, keyed by (model, messages, parameters, salt). Re-running a stage costs
  nothing and interrupted runs resume. The salt carries the run id so that repeated runs are independent.
* Every uncached call is logged (prompt, response, tokens, latency, list-price cost) to runs/<...>/calls.jsonl
  and added to a cost ledger. A hard spending cap stops paid calls before the budget is exceeded.
"""
import json
import os
import random
import threading
import time

import requests

from .common import cfg, out_dir, sha, read_json, write_json, append_jsonl

_lock = threading.Lock()
_ledger = None


class BudgetExceeded(RuntimeError):
    pass


class LLMError(RuntimeError):
    pass


# ----------------------------------------------------------------------------- models / providers
def model_cfg(name):
    for m in cfg()["models"]:
        if m["name"] == name:
            return m
    raise KeyError(f"model {name} is not configured in config.yaml")


def provider(name):
    return model_cfg(name).get("provider", "openai")


PROVIDERS = {
    "openai": {"base": "https://api.openai.com/v1", "key": "OPENAI_API_KEY"},
    "groq": {"base": "https://api.groq.com/openai/v1", "key": "GROQ_API_KEY"},
    "ollama": {"base": None, "key": None},
}


def _base(prov):
    if prov == "ollama":
        return os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434/v1")
    return PROVIDERS[prov]["base"]


# ----------------------------------------------------------------------------- cost ledger
def _ledger_path():
    return out_dir() / "cost_ledger.json"


def ledger():
    global _ledger
    if _ledger is None:
        _ledger = read_json(_ledger_path(), {"total_usd": 0.0, "calls": 0, "by_model": {}, "by_stage": {}})
    return _ledger


def flush_ledger():
    with _lock:
        write_json(_ledger_path(), ledger())


def cost_of(model, usage):
    m = model_cfg(model)
    p = m.get("price", {"input": 0, "output": 0})
    inp = usage.get("input_tokens", 0)
    cached = usage.get("cached_input_tokens", 0)
    out = usage.get("output_tokens", 0)
    return ((inp - cached) * p.get("input", 0) + cached * p.get("cached_input", p.get("input", 0))
            + out * p.get("output", 0)) / 1e6


def _record(model, usage, stage, cost):
    with _lock:
        L = ledger()
        L["total_usd"] += cost
        L["calls"] += 1
        bm = L["by_model"].setdefault(model, {"usd": 0.0, "calls": 0, "input_tokens": 0, "output_tokens": 0,
                                              "cached_input_tokens": 0})
        bm["usd"] += cost
        bm["calls"] += 1
        for k in ("input_tokens", "output_tokens", "cached_input_tokens"):
            bm[k] += usage.get(k, 0)
        L["by_stage"][stage] = L["by_stage"].get(stage, 0.0) + cost
        if L["calls"] % 20 == 0:
            write_json(_ledger_path(), L)


def _check_budget(model):
    if provider(model) != "openai" and not model_cfg(model).get("price"):
        return
    cap = cfg().get("max_total_cost_usd", 10)
    if ledger()["total_usd"] >= cap:
        flush_ledger()
        raise BudgetExceeded(f"cost cap reached: ${ledger()['total_usd']:.2f} >= ${cap}. "
                             "Raise max_total_cost_usd in config.yaml to continue.")


# ----------------------------------------------------------------------------- rate limiting (free tiers)
_rate = {}


def _throttle(model):
    rpm = model_cfg(model).get("rpm")
    if not rpm:
        return
    with _lock:
        now = time.time()
        q = [t for t in _rate.get(model, []) if now - t < 60]
        wait = 0 if len(q) < rpm else 60 - (now - q[0]) + 0.5
        _rate[model] = q
    if wait > 0:
        time.sleep(wait)
    with _lock:
        _rate.setdefault(model, []).append(time.time())


# ----------------------------------------------------------------------------- HTTP
def _post(url, headers, body, timeout):
    delay, last = 2.0, None
    for attempt in range(8):
        try:
            r = requests.post(url, headers=headers, json=body, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}: {r.text[:400]}"
            if r.status_code in (400, 401, 403, 404, 422):
                raise LLMError(last)
            if r.status_code == 429:
                ra = r.headers.get("retry-after")
                if ra:
                    try:
                        delay = max(delay, float(ra))
                    except ValueError:
                        pass
        except requests.RequestException as e:
            last = str(e)
        time.sleep(delay + random.random())
        delay = min(delay * 2, 90)
    raise LLMError(f"call failed after retries: {last}")


def _reasoning(model):
    return bool(model_cfg(model).get("reasoning", False))


def _call(model, messages, temperature, max_tokens):
    m = model_cfg(model)
    prov = m.get("provider", "openai")
    api_model = m.get("api_name", model)
    body = {"model": api_model, "messages": messages}
    if _reasoning(model):
        body["max_completion_tokens"] = max(max_tokens, 4096)
        if m.get("reasoning_effort"):
            body["reasoning_effort"] = m["reasoning_effort"]
    else:
        body["temperature"] = temperature
        body["max_tokens"] = max_tokens
    if m.get("seed") is not None:
        body["seed"] = m["seed"]
    headers = {"Content-Type": "application/json"}
    key_env = PROVIDERS[prov]["key"]
    if key_env:
        key = os.environ.get(key_env)
        if not key:
            raise LLMError(f"{key_env} is not set (add it to .env)")
        headers["Authorization"] = f"Bearer {key}"
    r = _post(_base(prov) + "/chat/completions", headers, body, timeout=m.get("timeout", 240))
    u = r.get("usage") or {}
    usage = {"input_tokens": u.get("prompt_tokens", 0), "output_tokens": u.get("completion_tokens", 0),
             "cached_input_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0,
             "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0}
    choice = r["choices"][0]
    text = choice["message"].get("content") or ""
    return text, usage, choice.get("finish_reason"), r.get("model", api_model)


# ----------------------------------------------------------------------------- dummy (offline tests)
_DUMMY = None


def set_dummy(fn):
    global _DUMMY
    _DUMMY = fn


def chat(model, messages, *, system=None, temperature=None, max_tokens=4000, stage="misc", salt=None,
         log_path=None, meta=None):
    """Returns dict(text, usage, cost, latency_s, cached, model, finish_reason)."""
    msgs = ([{"role": "system", "content": system}] if system else []) + list(messages)
    temperature = cfg().get("temperature", 0.3) if temperature is None else temperature
    params = {"temperature": temperature, "max_tokens": max_tokens}
    key = sha({"model": model, "messages": msgs, "params": params, "salt": salt}, 32)
    cf = out_dir("cache", "llm", key[:2]) / f"{key}.json"
    hit = read_json(cf)
    if hit is not None:
        hit["cached"] = True
        return hit
    t0 = time.time()
    if model.startswith("dummy"):
        text = _DUMMY(model, msgs, meta or {}) if _DUMMY else "```python\n# no-op\n```"
        usage = {"input_tokens": sum(len(m["content"]) for m in msgs) // 4, "output_tokens": len(text) // 4,
                 "cached_input_tokens": 0}
        finish, served = "stop", model
        cost = 0.0
    else:
        _check_budget(model)
        _throttle(model)
        text, usage, finish, served = _call(model, msgs, temperature, max_tokens)
        cost = cost_of(model, usage)
        _record(model, usage, stage, cost)
    res = {"text": text, "usage": usage, "cost": cost, "latency_s": round(time.time() - t0, 3), "model": model,
           "served_model": served, "finish_reason": finish, "stage": stage, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    write_json(cf, res)
    if log_path:
        append_jsonl(log_path, {"key": key, "stage": stage, "meta": meta, "messages": msgs, **res})
    res["cached"] = False
    return res
