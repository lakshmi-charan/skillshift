"""Pilot report: observed cost, call counts, failures and headline metrics, plus a projection for the main study."""
import json
from collections import Counter, defaultdict

import numpy as np

from . import bench, llm
from .analysis import summarize, load_records
from .common import out_dir, read_json, read_jsonl, write_json, cfg
from .runner import split_of


def _usage(model, methods, families):
    rows = []
    for m in methods:
        for f in families:
            rows.extend(read_json(out_dir(model, m, "run0", f) / "usage.json", []) or [])
    return rows


def pilot_report(model, methods, families):
    s, comp, tasks, costs = summarize(model, methods, [0], families, splits=("dev",))
    usage = _usage(model, methods, families)
    by_m = defaultdict(lambda: {"calls": 0, "cost": 0.0, "in": 0, "out": 0, "task_cost": 0.0, "adapt_cost": 0.0,
                                "latency": [], "truncated": 0})
    for u in usage:
        b = by_m[u["method"]]
        b["calls"] += 1
        b["cost"] += u["cost"]
        b["in"] += u["input_tokens"]
        b["out"] += u["output_tokens"]
        b["latency"].append(u["latency_s"])
        b["truncated"] += int(u.get("finish_reason") == "length")
        if u["stage"] == "task":
            b["task_cost"] += u["cost"]
        else:
            b["adapt_cost"] += u["cost"]
    fails = read_jsonl(out_dir() / "failures.jsonl")
    # projection: dev events processed vs all events, per family
    n_dev = n_all = 0
    for f in families:
        for st in bench.family(f)["states"][1:]:
            n_all += 1
            n_dev += split_of(st["date"]) == "dev"
    n_s0 = len(families)
    pilot_total = sum(b["cost"] for b in by_m.values())
    scale = (n_all + n_s0) / max(1, n_dev + n_s0)
    rep = {"model": model, "families": families, "methods": methods, "dev_events": n_dev, "all_events": n_all,
           "pilot_cost_usd": round(pilot_total, 4),
           "projected_full_timeline_one_run_usd": round(pilot_total * scale, 2),
           "projected_three_runs_usd": round(pilot_total * scale * 3, 2),
           "failures": len(fails), "per_method": {}}
    for m in methods:
        b = by_m[m]
        r = s["by_split"]["dev"].get(m, {})
        rep["per_method"][m] = {
            "calls": b["calls"], "cost": round(b["cost"], 4), "adapt_cost": round(b["adapt_cost"], 4),
            "task_cost": round(b["task_cost"], 4), "input_tokens": b["in"], "output_tokens": b["out"],
            "median_latency_s": round(float(np.median(b["latency"])), 2) if b["latency"] else None,
            "truncated": b["truncated"],
            **{k: (round(v["mean"], 3) if v["n"] else None) for k, v in r.items() if isinstance(v, dict)}}
    write_json(out_dir("results") / f"pilot_{model}.json", rep)
    print(json.dumps(rep, indent=1))
    return rep
