"""Drives each (model, method, run, family) through the family's dated states and records everything.

For each state after s0:  hidden-test evaluation of the library BEFORE adaptation (in the new runtime),
adaptation, hidden-test evaluation AFTER adaptation, and downstream tasks solved with the adapted library.
All raw test outputs, LLM calls, library snapshots and decisions are saved under runs/.
"""
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import bench, llm, prompts
from .common import cfg, out_dir, write_json, read_json, append_jsonl, sha
from .library import initial_library, code_map, extract_blocks
from .methods import METHODS, Ctx


def split_of(date):
    return "dev" if str(date) <= str(cfg().get("dev_cutoff", "2024-06-30")) else "test"


def eval_library(fid, sid, lib):
    """Hidden tests for every skill of the family, with the library's active skills importable."""
    cm = code_map(lib)
    out = {}
    for sk in bench.family(fid)["skills"]:
        res = bench.run_hidden(fid, sk["id"], sid, cm.get(sk["id"]), library=cm)
        out[sk["id"]] = {"cases": [{k: c.get(k) for k in ("name", "component", "kind", "passed", "error", "missing")}
                                   for c in res.get("cases", [])],
                         "import_error": res.get("import_error"), "fatal": res.get("fatal")}
    return out


def solve_task(fid, sid, task, method, ms, ctx):
    tc = method.task_context(fid, sid, ms)
    user = prompts.task_prompt(fid, sid, task, skills=tc["skills"], tombstones=tc["tombstones"], docs=tc["docs"])
    txt = ctx.chat(prompts.TASK_SYSTEM, user, "task", fid, sid, task["id"], max_tokens=6000,
                   share_key=["task", fid, sid, task["id"], sha(user)])
    b = extract_blocks(txt)
    code = b["_blocks"][-1] if b["_blocks"] else None
    lib = code_map(ms["lib"]) if method.uses_library else {}
    res = bench.run_task(fid, task["id"], sid, code, library=lib)
    return {"task": task["id"], "code": code, "prompt_sha": sha(user),
            "cases": [{k: c.get(k) for k in ("name", "component", "kind", "passed", "error")}
                      for c in res.get("cases", [])],
            "import_error": res.get("import_error"), "fatal": res.get("fatal")}


def run_family(model, method_name, run, fid, max_split="test"):
    method = METHODS[method_name]()
    base = out_dir(model, method_name, f"run{run}", fid)
    done_path = base / "done.json"
    if read_json(done_path, {}).get("max_split") in (max_split, "test"):
        return read_json(done_path)
    ctx = Ctx(model, method_name, run, base / "calls.jsonl", llm.chat)
    ctx.cache_method = getattr(method, "cache_as", method_name)
    fam = bench.family(fid)
    states = [s for s in fam["states"] if s["index"] == 0 or split_of(s["date"]) == "dev" or max_split == "test"]
    t0 = time.time()
    lib0 = initial_library(fid)
    ms = method.init(fid, lib0, ctx)
    records = []
    s0 = states[0]["id"]
    rec0 = {"model": model, "method": method_name, "run": run, "family": fid, "state": s0, "date": states[0]["date"],
            "split": "s0", "event": None,
            "post": eval_library(fid, s0, ms["lib"]) if method.uses_library else None,
            "tasks": [solve_task(fid, s0, t, method, ms, ctx) for t in bench.tasks(fid)]}
    records.append(rec0)
    write_json(base / f"library_{s0}.json", ms)
    for st in states[1:]:
        sid = st["id"]
        pre = eval_library(fid, sid, ms["lib"]) if method.uses_library else None
        n_before = len(ctx.usage)
        ta = time.time()
        ms = method.adapt(fid, sid, ms, ctx)
        adapt_s = time.time() - ta
        post = eval_library(fid, sid, ms["lib"]) if method.uses_library else None
        tasks = [solve_task(fid, sid, t, method, ms, ctx) for t in bench.tasks(fid)]
        adapt_calls = [u for u in ctx.usage[n_before:] if u["stage"] != "task"]
        records.append({"model": model, "method": method_name, "run": run, "family": fid, "state": sid,
                        "date": st["date"], "split": split_of(st["date"]), "event": st["event"]["id"],
                        "event_kind": st["event"]["kind"], "pre": pre, "post": post, "tasks": tasks,
                        "adapt_seconds": round(adapt_s, 2), "adapt_calls": len(adapt_calls),
                        "adapt_input_tokens": sum(u["input_tokens"] for u in adapt_calls),
                        "adapt_output_tokens": sum(u["output_tokens"] for u in adapt_calls),
                        "adapt_cost": sum(u["cost"] for u in adapt_calls),
                        "status": {k: v["status"] for k, v in ms["lib"].items()},
                        "tombstones": len(ms.get("tombstones") or [])})
        write_json(base / f"library_{sid}.json", ms)
    write_json(base / "records.json", records)
    write_json(base / "usage.json", ctx.usage)
    if hasattr(method, "parse_log"):
        write_json(base / "parse_log.json", method.parse_log)
    summary = {"max_split": max_split, "seconds": round(time.time() - t0, 1), "calls": len(ctx.usage),
               "cost": sum(u["cost"] for u in ctx.usage)}
    write_json(done_path, summary)
    return summary


def run_all(models, methods, runs, families, max_split="dev", workers=4):
    jobs = [(m, me, r, f) for m in models for r in runs for me in methods for f in families]
    print(f"{len(jobs)} jobs ({len(models)} models x {len(methods)} methods x {len(runs)} runs x {len(families)} families)")
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_family, *j, max_split): j for j in jobs}
        for i, f in enumerate(as_completed(futs)):
            j = futs[f]
            try:
                s = f.result()
                results.append((j, s))
                print(f"  [{i + 1}/{len(jobs)}] {j}: {s.get('calls')} calls, ${s.get('cost', 0):.4f}, {s.get('seconds')}s "
                      f"| total ${llm.ledger()['total_usd']:.3f}", flush=True)
            except llm.BudgetExceeded as e:
                print("BUDGET STOP:", e)
                ex.shutdown(cancel_futures=True)
                raise
            except Exception as e:  # keep going; record the failure
                append_jsonl(out_dir() / "failures.jsonl", {"job": j, "error": repr(e), "tb": traceback.format_exc()})
                print(f"  [{i + 1}/{len(jobs)}] {j}: FAILED {e!r}", flush=True)
    llm.flush_ledger()
    return results
