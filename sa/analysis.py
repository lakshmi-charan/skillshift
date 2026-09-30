"""Metrics, uncertainty and tables from saved run records.

Component outcome categories (library level, per event, computed from hidden tests BEFORE and AFTER adaptation):
  valid/policy component: kept (pass->pass), lost (pass->fail: accidental loss), repaired (fail->pass),
                          unrepaired (fail->fail)
  obsolete component:     retired (prohibited behaviour absent after adaptation) or persisting
Downstream task outcomes: success (all cases pass), functional (all non-policy cases pass), violation (a policy case fails).
Uncertainty: cluster bootstrap over (family, event) clusters, resampling runs within clusters.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import bench
from .common import out_dir, read_json, write_json, cfg


def load_records(model, methods=None, runs=None, families=None):
    base = out_dir(model)
    recs = []
    for mdir in sorted(p for p in base.iterdir() if p.is_dir()):
        if methods and mdir.name not in methods:
            continue
        for rdir in sorted(mdir.glob("run*")):
            if runs is not None and int(rdir.name[3:]) not in runs:
                continue
            for fdir in sorted(rdir.iterdir()):
                if families and fdir.name not in families:
                    continue
                r = read_json(fdir / "records.json")
                if r:
                    recs.extend(r)
    return recs


def _comp_status(evalres):
    """skill -> component -> (kind, passed_all)."""
    out = {}
    for kid, v in (evalres or {}).items():
        d = {}
        for c in v["cases"]:
            k, p = c["component"], bool(c["passed"])
            if k in d:
                d[k] = (d[k][0], d[k][1] and p)
            else:
                d[k] = (c["kind"], p)
        out[kid] = d
    return out


def component_rows(records):
    labels = read_json(out_dir() / "labels.json") or []
    lab = {(r["family"], r["event"], r["skill"], r["component"]): r["label"] for r in labels}
    rows = []
    for rec in records:
        if rec.get("event") is None or rec.get("pre") is None:
            continue
        pre, post = _comp_status(rec["pre"]), _comp_status(rec["post"])
        for kid, comps in post.items():
            for comp, (kind, ppost) in comps.items():
                ppre = pre.get(kid, {}).get(comp, (kind, False))[1]
                if kind == "obsolete":
                    cat = "retired" if ppost else "persisting"
                else:
                    cat = {(True, True): "kept", (True, False): "lost", (False, True): "repaired",
                           (False, False): "unrepaired"}[(ppre, ppost)]
                rows.append({"model": rec["model"], "method": rec["method"], "run": rec["run"],
                             "family": rec["family"], "event": rec["event"], "split": rec["split"],
                             "event_kind": rec.get("event_kind"), "skill": kid, "component": comp, "kind": kind,
                             "label": lab.get((rec["family"], rec["event"], kid, comp)), "pre": ppre, "post": ppost,
                             "cat": cat})
    return rows


def task_rows(records):
    rows = []
    for rec in records:
        for t in rec["tasks"]:
            cases = t["cases"]
            ok = bool(cases) and all(c["passed"] for c in cases) and not t.get("import_error")
            func = bool(cases) and all(c["passed"] for c in cases if c["kind"] != "policy") and not t.get("import_error")
            pol = [c for c in cases if c["kind"] == "policy"]
            viol = any(not c["passed"] for c in pol) if pol else None
            rows.append({"model": rec["model"], "method": rec["method"], "run": rec["run"], "family": rec["family"],
                         "state": rec["state"], "event": rec.get("event"), "split": rec["split"],
                         "event_kind": rec.get("event_kind"), "task": t["task"], "success": ok, "functional": func,
                         "violation": viol, "no_code": t.get("code") is None})
    return rows


def cost_rows(records):
    rows = []
    for rec in records:
        if rec.get("event") is None:
            continue
        rows.append({k: rec.get(k) for k in ("model", "method", "run", "family", "event", "split", "adapt_calls",
                                               "adapt_input_tokens", "adapt_output_tokens", "adapt_cost",
                                               "adapt_seconds")})
    return rows


# ----------------------------------------------------------------------------- metrics with cluster bootstrap
def _rate(rows, num, den):
    n = sum(1 for r in rows if den(r))
    return (sum(1 for r in rows if den(r) and num(r)) / n) if n else float("nan"), n


METRICS = {
    "retention": (lambda r: r["cat"] == "kept", lambda r: r["cat"] in ("kept", "lost")),
    "accidental_loss": (lambda r: r["cat"] == "lost", lambda r: r["cat"] in ("kept", "lost")),
    "repair": (lambda r: r["cat"] == "repaired", lambda r: r["cat"] in ("repaired", "unrepaired")),
    "retirement": (lambda r: r["cat"] == "retired", lambda r: r["kind"] == "obsolete"),
    "obsolete_persistence": (lambda r: r["cat"] == "persisting", lambda r: r["kind"] == "obsolete"),
    "policy_violation_lib": (lambda r: not r["post"], lambda r: r["kind"] == "policy"),
    "component_correct": (lambda r: r["post"], lambda r: True),
}
TASK_METRICS = {
    "task_success": (lambda r: r["success"], lambda r: not r["no_code"] or True),
    "task_functional": (lambda r: r["functional"], lambda r: True),
    "task_policy_violation": (lambda r: r["violation"] is True, lambda r: r["violation"] is not None),
}


def bootstrap(rows, metric, cluster_keys=("family", "event"), n_boot=2000, seed=0):
    num, den = metric
    point, n = _rate(rows, num, den)
    if n == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in cluster_keys)].append(r)
    keys = list(groups)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(keys), len(keys))
        num_s = den_s = 0
        for i in pick:
            g = groups[keys[i]]
            d = [r for r in g if den(r)]
            den_s += len(d)
            num_s += sum(1 for r in d if num(r))
        if den_s:
            vals.append(num_s / den_s)
    lo, hi = (np.percentile(vals, [2.5, 97.5]) if vals else (float("nan"), float("nan")))
    return {"mean": point, "lo": float(lo), "hi": float(hi), "n": n}


def paired_diff(rows, metric, a, b, cluster_keys=("family", "event"), n_boot=2000, seed=0):
    """Bootstrap CI of metric(a) - metric(b) using the same resampled clusters for both methods."""
    num, den = metric
    groups = defaultdict(lambda: {a: [], b: []})
    for r in rows:
        if r["method"] in (a, b):
            groups[tuple(r[k] for k in cluster_keys)][r["method"]].append(r)
    keys = [k for k, g in groups.items() if g[a] and g[b]]
    if not keys:
        return None

    def rate(sel, m):
        d = [r for k in sel for r in groups[k][m] if den(r)]
        return (sum(1 for r in d if num(r)) / len(d)) if d else np.nan
    point = rate(keys, a) - rate(keys, b)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        sel = [keys[i] for i in rng.integers(0, len(keys), len(keys))]
        v = rate(sel, a) - rate(sel, b)
        if not np.isnan(v):
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5]) if vals else (np.nan, np.nan)
    return {"diff": float(point), "lo": float(lo), "hi": float(hi), "clusters": len(keys),
            "p_le_0": float(np.mean(np.array(vals) <= 0)) if vals else np.nan}


def summarize(model, methods=None, runs=None, families=None, splits=("dev", "test")):
    recs = load_records(model, methods, runs, families)
    comp, tasks, costs = component_rows(recs), task_rows(recs), cost_rows(recs)
    methods = methods or sorted({r["method"] for r in recs})
    out = {"model": model, "n_records": len(recs), "by_split": {}}
    for sp in splits:
        res = {}
        for m in methods:
            cr = [r for r in comp if r["method"] == m and r["split"] == sp]
            tr = [r for r in tasks if r["method"] == m and r["split"] == sp]
            kr = [r for r in costs if r["method"] == m and r["split"] == sp]
            res[m] = {k: bootstrap(cr, v) for k, v in METRICS.items()}
            res[m].update({k: bootstrap(tr, v) for k, v in TASK_METRICS.items()})
            res[m]["adapt_cost_per_event"] = float(np.mean([r["adapt_cost"] or 0 for r in kr])) if kr else 0.0
            res[m]["adapt_calls_per_event"] = float(np.mean([r["adapt_calls"] or 0 for r in kr])) if kr else 0.0
            res[m]["adapt_tokens_per_event"] = float(np.mean([(r["adapt_input_tokens"] or 0) + (r["adapt_output_tokens"] or 0)
                                                              for r in kr])) if kr else 0.0
            res[m]["adapt_seconds_per_event"] = float(np.mean([r["adapt_seconds"] or 0 for r in kr])) if kr else 0.0
        out["by_split"][sp] = res
    return out, comp, tasks, costs


def main():
    model = cfg()["primary_model"]
    s, comp, tasks, costs = summarize(model)
    d = out_dir("results", model)
    write_json(d / "summary.json", s)
    write_json(d / "component_rows.json", comp)
    write_json(d / "task_rows.json", tasks)
    write_json(d / "cost_rows.json", costs)
    print(json.dumps({sp: {m: {k: round(v["mean"], 3) if isinstance(v, dict) else round(v, 4)
                               for k, v in r.items()} for m, r in res.items()} for sp, res in s["by_split"].items()},
                     indent=1)[:6000])
