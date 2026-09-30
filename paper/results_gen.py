"""Compute every reported number from saved records; write results.json + evidence index; render figures.
Usage: python results_gen.py <runs_dir> <out_dir> [split]"""
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
RUNS, OUT = sys.argv[1], Path(sys.argv[2])
SPLIT = sys.argv[3] if len(sys.argv) > 3 else "test"
os.environ["SA_RUNS"] = RUNS
from sa import analysis as A  # noqa: E402
from sa import figures as F  # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)
MAIN = ["no_skills", "static", "doc_retrieval", "version_aware", "regenerate", "regression_gated", "regression_refresh",
        "skill_ledger"]
ABL = ["skill_ledger", "ledger_no_quarantine", "ledger_no_tombstones", "ledger_nonselective"]
POSTHOC = ["skill_ledger_robust"]
LIB_METRICS = ["retention", "accidental_loss", "repair", "retirement", "policy_violation_lib", "component_correct"]
TASK_METRICS = ["task_success", "task_functional", "task_policy_violation"]
EVID = []   # evidence index rows


def ev(key, value, source, how):
    EVID.append({"key": key, "value": value, "source": source, "computation": how})
    return value


def fmt(v, pct=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "n/a"
    return f"{100 * v:.1f}" if pct else f"{v:.3f}"


def ci(b):
    if not b or not b.get("n"):
        return "n/a"
    return f"{100 * b['mean']:.1f} [{100 * b['lo']:.1f}, {100 * b['hi']:.1f}]"


def summarize_model(model, methods, runs=None, splits=(SPLIT,)):
    recs = A.load_records(model, methods, runs)
    comp, tasks, costs = A.component_rows(recs), A.task_rows(recs), A.cost_rows(recs)
    return recs, comp, tasks, costs


def block(comp, tasks, costs, methods, split, kind=None):
    res = {}
    for m in methods:
        cr = [r for r in comp if r["method"] == m and r["split"] == split and (kind is None or r["event_kind"] == kind)]
        tr = [r for r in tasks if r["method"] == m and r["split"] == split and (kind is None or r["event_kind"] == kind)]
        kr = [r for r in costs if r["method"] == m and r["split"] == split and (kind is None or
                                                                                 _kind_of(r["event"]) == kind)]
        d = {k: A.bootstrap(cr, v) for k, v in A.METRICS.items()}
        d.update({k: A.bootstrap(tr, v) for k, v in A.TASK_METRICS.items()})
        d["n_components"] = len(cr)
        d["n_task_instances"] = len(tr)
        d["cost_per_event"] = float(np.mean([r["adapt_cost"] or 0 for r in kr])) if kr else 0.0
        d["adapt_cost_per_event"] = d["cost_per_event"]   # key read by sa.figures.cost_scatter
        d["calls_per_event"] = float(np.mean([r["adapt_calls"] or 0 for r in kr])) if kr else 0.0
        d["tokens_per_event"] = float(np.mean([(r["adapt_input_tokens"] or 0) + (r["adapt_output_tokens"] or 0)
                                               for r in kr])) if kr else 0.0
        d["seconds_per_event"] = float(np.mean([r["adapt_seconds"] or 0 for r in kr])) if kr else 0.0
        res[m] = d
    return res


_KIND = {}


def _kind_of(event):
    return _KIND.get(event)


def paired_cost(costs, a, b, split, n_boot=2000, seed=0):
    """Paired cluster bootstrap of mean adaptation cost per event, a - b, over (family, event) clusters."""
    g = defaultdict(lambda: {a: [], b: []})
    for r in costs:
        if r["split"] == split and r["method"] in (a, b):
            g[(r["family"], r["event"])][r["method"]].append(r["adapt_cost"] or 0.0)
    keys = [k for k, v in g.items() if v[a] and v[b]]
    if not keys:
        return None

    def val(sel):
        xa = [x for k in sel for x in g[k][a]]
        xb = [x for k in sel for x in g[k][b]]
        return float(np.mean(xa) - np.mean(xb))
    rng = np.random.default_rng(seed)
    vals = [val([keys[i] for i in rng.integers(0, len(keys), len(keys))]) for _ in range(n_boot)]
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {"diff": val(keys), "lo": float(lo), "hi": float(hi), "clusters": len(keys),
            "p_ge_0": float(np.mean(np.array(vals) >= 0))}


def extras(comp, tasks, costs, present, labels):
    """Hypothesis contrasts exactly as preregistered (event-kind restrictions included) and descriptive breakdowns."""
    ex = {}
    new_obs = {(r["family"], r["event"], r["skill"], r["component"]) for r in labels if r["label"] == "retire"}
    ct = [r for r in comp if r["split"] == SPLIT]
    tt = [r for r in tasks if r["split"] == SPLIT]
    pol_c = [r for r in ct if r["event_kind"] == "policy"]
    pol_t = [r for r in tt if r["event_kind"] == "policy"]
    tool_c = [r for r in ct if r["event_kind"] == "tool"]
    hyp = {}
    L = "skill_ledger"
    for other in [m for m in present if m != L]:
        h = {"retirement_policy": A.paired_diff(pol_c, A.METRICS["retirement"], L, other),
             "task_violation_policy": A.paired_diff(pol_t, A.TASK_METRICS["task_policy_violation"], L, other),
             "task_violation_all": A.paired_diff(tt, A.TASK_METRICS["task_policy_violation"], L, other),
             "repair_tool": A.paired_diff(tool_c, A.METRICS["repair"], L, other),
             "repair_policy": A.paired_diff(pol_c, A.METRICS["repair"], L, other),
             "accidental_loss": A.paired_diff(ct, A.METRICS["accidental_loss"], L, other),
             "accidental_loss_tool": A.paired_diff(tool_c, A.METRICS["accidental_loss"], L, other),
             "component_correct": A.paired_diff(ct, A.METRICS["component_correct"], L, other),
             "task_success": A.paired_diff(tt, A.TASK_METRICS["task_success"], L, other),
             "cost": paired_cost(costs, L, other, SPLIT)}
        hyp[other] = h
    if "skill_ledger_robust" in present:
        R = "skill_ledger_robust"
        hyp["robust_minus"] = {}
        for other in [m for m in present if m != R]:
            hyp["robust_minus"][other] = {
                "retirement": A.paired_diff(ct, A.METRICS["retirement"], R, other),
                "retirement_policy": A.paired_diff(pol_c, A.METRICS["retirement"], R, other),
                "repair": A.paired_diff(ct, A.METRICS["repair"], R, other),
                "accidental_loss": A.paired_diff(ct, A.METRICS["accidental_loss"], R, other),
                "task_violation_all": A.paired_diff(tt, A.TASK_METRICS["task_policy_violation"], R, other),
                "task_success": A.paired_diff(tt, A.TASK_METRICS["task_success"], R, other),
                "component_correct": A.paired_diff(ct, A.METRICS["component_correct"], R, other),
                "cost": paired_cost(costs, R, other, SPLIT)}
    ex["hyp"] = hyp
    # obsolete components: newly prohibited at this event vs prohibited earlier (recurrence check)
    ob = {}
    for m in present:
        rows = [r for r in ct if r["method"] == m and r["kind"] == "obsolete"]
        new = [r for r in rows if (r["family"], r["event"], r["skill"], r["component"]) in new_obs]
        old = [r for r in rows if (r["family"], r["event"], r["skill"], r["component"]) not in new_obs]
        ob[m] = {"new_retired": sum(r["cat"] == "retired" for r in new), "new_total": len(new),
                 "carried_retired": sum(r["cat"] == "retired" for r in old), "carried_total": len(old)}
    ex["obsolete_breakdown"] = ob
    # where accidental losses occur
    ex["loss_by_event"] = {m: dict(Counter(f"{r['event']}|{r['family']}" for r in ct
                                           if r["method"] == m and r["cat"] == "lost")) for m in present}
    ex["n_runs_by_method"] = {m: len({r["run"] for r in ct if r["method"] == m}) for m in present}
    # per-family share of components correct after adaptation
    fams = sorted({r["family"] for r in ct})
    ex["family_correct"] = {m: {f: A._rate([r for r in ct if r["method"] == m and r["family"] == f],
                                           *A.METRICS["component_correct"])[0] for f in fams} for m in present}
    ex["family_task_success"] = {m: {f: A._rate([r for r in tt if r["method"] == m and r["family"] == f],
                                                *A.TASK_METRICS["task_success"])[0] for f in fams} for m in present}
    return ex


def main():
    out = {"split": SPLIT, "models": {}}
    labels = json.loads((Path(RUNS) / "labels.json").read_text())
    for r in labels:
        _KIND[r["event"]] = r["kind_event"]
    for model, methods in (("gpt-4.1-mini", MAIN + ABL[1:] + POSTHOC), ("gpt-5.4-nano", MAIN + POSTHOC),
                           ("gpt-5.4-mini", MAIN + POSTHOC)):
        if not (Path(RUNS) / model).exists():
            continue
        recs, comp, tasks, costs = summarize_model(model, methods)
        present = sorted({r["method"] for r in recs})
        mres = {"methods": present, "n_runs": len({r["run"] for r in recs}),
                "overall": block(comp, tasks, costs, present, SPLIT),
                "tool": block(comp, tasks, costs, present, SPLIT, "tool"),
                "policy": block(comp, tasks, costs, present, SPLIT, "policy")}
        if SPLIT == "test":
            mres["dev_overall"] = block(comp, tasks, costs, present, "dev")
        # paired contrasts vs skill_ledger
        pc = {}
        for other in [m for m in present if m != "skill_ledger"]:
            pc[other] = {}
            for met in ("retention", "repair", "retirement", "accidental_loss"):
                rows = [r for r in comp if r["split"] == SPLIT]
                pc[other][met] = A.paired_diff(rows, A.METRICS[met], "skill_ledger", other)
            for met in ("task_success", "task_policy_violation"):
                rows = [r for r in tasks if r["split"] == SPLIT]
                pc[other][met] = A.paired_diff(rows, A.TASK_METRICS[met], "skill_ledger", other)
        mres["paired_vs_ledger"] = pc
        # outcome composition per method (counts)
        mres["categories"] = {m: dict(Counter(r["cat"] for r in comp if r["method"] == m and r["split"] == SPLIT))
                              for m in present}
        # per-event retirement detail
        mres["obsolete_detail"] = [
            {k: r[k] for k in ("method", "run", "family", "event", "skill", "component", "cat")}
            for r in comp if r["kind"] == "obsolete" and r["split"] == SPLIT]
        mres["extras"] = extras(comp, tasks, costs, present, labels)
        # skill status after the event for accidental losses (withheld vs edited)
        stat = {(r["method"], r["run"], r["family"], r["event"]): r.get("status") or {} for r in recs if r.get("event")}
        mres["extras"]["loss_skill_status"] = {
            m: dict(Counter(stat[(m, r["run"], r["family"], r["event"])].get(r["skill"], "absent") for r in comp
                            if r["method"] == m and r["cat"] == "lost" and r["split"] == SPLIT)) for m in present}
        tt = [r for r in tasks if r["split"] == SPLIT]
        mres["extras"]["other_contrasts"] = {
            f"{a}-{b}/{k}": A.paired_diff(tt, A.TASK_METRICS[k], a, b)
            for a, b in (("doc_retrieval", "no_skills"), ("static", "no_skills"), ("version_aware", "no_skills"),
                         ("regression_refresh", "no_skills"), ("regenerate", "no_skills"))
            if a in present and b in present for k in ("task_success", "task_policy_violation")}
        out["models"][model] = mres
        # figures for this model
        tag = model.replace(".", "")
        S = mres["overall"]
        meth = [m for m in MAIN if m in present]
        lib_meth = [m for m in meth if m != "no_skills"]
        F.dot_panels(S, lib_meth, ["retention", "repair", "retirement"],
                     ["Retention of still-valid behaviour", "Repair after breakage", "Retirement of prohibited behaviour"],
                     OUT / f"fig_lib_{tag}.png")
        F.dot_panels(S, meth, ["task_success", "task_policy_violation"],
                     ["Downstream task success", "Downstream policy violations"], OUT / f"fig_task_{tag}.png", width=6.4)
        F.cost_scatter(S, lib_meth, "component_correct", OUT / f"fig_cost_{tag}.png",
                       "Components correct after adaptation")
        F.outcome_stack(comp, lib_meth, OUT / f"fig_stack_{tag}.png", split=SPLIT)
        if model == "gpt-4.1-mini":
            ab = [m for m in ABL if m in present]
            if len(ab) > 1:
                F.dot_panels(S, ab, ["retention", "repair", "retirement", "task_policy_violation"],
                             ["Retention", "Repair", "Retirement", "Task policy violations"], OUT / "fig_ablation.png",
                             width=7.2)
    # evidence index: every headline value with its source
    for model, mres in out["models"].items():
        for part in ("overall", "tool", "policy"):
            for m, d in mres[part].items():
                for k in LIB_METRICS + TASK_METRICS:
                    b = d.get(k)
                    if b and b.get("n"):
                        ev(f"{model}/{SPLIT}/{part}/{m}/{k}", round(b["mean"], 4),
                           f"{Path(RUNS).name}/{model}/{m}/run*/<family>/records.json",
                           f"analysis.bootstrap over {b['n']} rows; 95% CI [{b['lo']:.4f}, {b['hi']:.4f}]")
                ev(f"{model}/{SPLIT}/{part}/{m}/cost_per_event", round(d["cost_per_event"], 6),
                   f"{Path(RUNS).name}/{model}/{m}/run*/<family>/records.json", "mean adapt_cost over events")
    (OUT / "results.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / "evidence_index.json").write_text(json.dumps(EVID, indent=1))
    print("wrote", OUT, "models:", list(out["models"]))


if __name__ == "__main__":
    main()
