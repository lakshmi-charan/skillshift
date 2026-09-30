"""Assemble the paper as JSON for build.js from static text, benchmark files and results.json.
Usage: python assemble.py <runs_dir> <res_dir> <out.json>"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from sa import bench  # noqa: E402
import content_static as S  # noqa: E402
import content_text as T  # noqa: E402
import content_results as C  # noqa: E402
from content_text import P, H1, H2  # noqa: E402

RUNS, RES, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])


def px(p):
    return list(Image.open(p).size)


def nums():
    n_sk = n_comp = n_task = 0
    ev = {}
    for f in S.FAM_ORDER:
        fam = bench.family(f)
        n_sk += len(fam["skills"])
        n_comp += sum(len(s["components"]) for s in fam["skills"])
        n_task += len(bench.tasks(f))
        for st in fam["states"][1:]:
            ev[st["event"]["id"]] = str(st["date"])
    return {"n_skills": n_sk, "n_components": n_comp, "n_tasks": n_task, "n_events": len(ev),
            "n_dev_events": sum(d <= "2024-06-30" for d in ev.values()),
            "n_test_events": sum(d > "2024-06-30" for d in ev.values()),
            "fig_timeline": str(RES / "fig_timeline.png"), "fig_timeline_px": px(RES / "fig_timeline.png")}


def appendix(r, N):
    A = "gpt-4.1-mini"
    freeze = json.loads((RUNS / "protocol_freeze.json").read_text())
    ledger = json.loads((RUNS / "cost_ledger.json").read_text())
    ph = json.loads((RUNS / "posthoc_runs.json").read_text()) if (RUNS / "posthoc_runs.json").exists() else []
    blocks = [{"type": "pagebreak"}, H1("Appendix A. Reproducibility"),
              H2("A.1 Artifact"),
              P("The artifact accompanying this paper contains: the benchmark (family definitions, skills, historical "
                "tests, hidden tests, reference solutions, downstream tasks and the verbatim change documents) with "
                "the scripts that fetch every document from its primary source; the experiment code (environment "
                "builder, sandboxed test runner, model client with cache and cost ledger, the eleven methods and the "
                "post-hoc variant, and the analysis); the frozen protocol; the Dockerfile; and all raw run records "
                "(per-state library snapshots, hidden-test outcomes before and after each adaptation, task "
                "solutions and their test outcomes, and the prompts, responses, token counts, costs and latencies of "
                "every model call). Every table and figure in this paper is regenerated from these records by two "
                "scripts; an evidence index maps every reported rate and cost to its source records and computation, "
                "and a results file holds every interval and paired contrast."),
              H2("A.2 Environment"),
              P("Experiments ran in a Docker image based on python:3.12-slim with uv 0.12.21. Each benchmark state "
                "declares a CPython minor version and exact package versions; the environment builder creates an "
                "isolated virtual environment per specification with uv, using uv-managed CPython builds pinned to "
                "3.9.25, 3.10.21, 3.11.16, 3.12.14, 3.13.15 and 3.14.7 (never a system interpreter), installing "
                "binary wheels only where possible, and resolving transitive dependencies as of 30 September 2026. "
                "Hidden and historical tests run in a subprocess of the target environment through a dependency-free "
                "runner with a 20-second per-test timeout and without API keys in its environment."),
              H2("A.3 Protocol freeze and amendment"),
              P(f"Before the first test-split event was run, a SHA-256 digest over the experiment code, the benchmark, "
                f"the configuration and the protocol was recorded ({freeze['files']} files; "
                f"`{freeze['sha256'][:16]}…`, full value in the artifact; {freeze['frozen_at']}). The main runner "
                "refuses to process test events if the digest differs. All results in Sections 7.1–7.8 were produced "
                "under this digest. Amendment A1 (Section 7.9) was added afterwards; its runs are restricted by the "
                "runner to the post-hoc variant and logged with the amended digest"
                + (f" (`{ph[0]['sha256'][:16]}…`)." if ph else ".")),
              H2("A.4 Models, settings and spend"),
              {"type": "table", "caption": "Models and settings. Prices are list prices per million tokens (input / cached "
               "input / output) used for all cost figures.",
               "header": ["Model", "Role", "Runs", "Methods", "Sampling", "Cutoff", "Price ($/M)"],
               "widths": [1.4, 1.2, 0.6, 1.8, 1.6, 1.1, 1.6], "size": 16, "leftcols": 2, "rows": [
                   ["gpt-4.1-mini", "primary", "3", "all 8 + 3 ablations", "temperature 0.3", "2024-06-01",
                    "0.40 / 0.10 / 1.60"],
                   ["gpt-5.4-nano", "robustness", "1", "all 8", "reasoning effort low", "2025-08-31",
                    "0.20 / 0.02 / 1.25"],
                   ["gpt-5.4-mini", "robustness", "1", "4 adaptive", "reasoning effort low", "2025-08-31",
                    "0.75 / 0.075 / 4.50"]]},
              P("Every model response is cached on disk under a key derived from the model, the messages, the sampling "
                "parameters and a salt that identifies the method, run, family, state, stage and attempt, so that an "
                "interrupted run resumes without repeating calls and independent runs do not share responses. Task "
                "prompts that are identical across methods share a response. Costs attributed to a method include "
                "calls served from the cache at their original price. The hard budget cap of US$35 was never reached. "
                f"Recorded spend for the main study and the post-hoc runs was US${ledger['total_usd']:.2f} ("
                + ", ".join(f"{k} US${v['usd']:.2f}" for k, v in ledger["by_model"].items())
                + "); development pilots were run separately beforehand."),
              H2("A.5 Commands"),
              P("With Docker available and an API key in a local environment file (never printed or logged), the full "
                "study is reproduced by the following commands, run in order:"),
              {"type": "list", "items": [
                  "`run.py check` and `run.py validate`: environment and key check; every family's references pass "
                  "their hidden tests.",
                  "`run.py labels`: ground-truth labels. `run.py pilot`: development split only.",
                  "`run.py freeze`: record the protocol digest.",
                  "`run.py main --model gpt-4.1-mini --runs 0,1,2 --ablations`",
                  "`run.py main --model gpt-5.4-nano --runs 0`",
                  "`run.py main --model gpt-5.4-mini --runs 0 --methods regenerate,regression_gated,"
                  "regression_refresh,skill_ledger`",
                  "`run.py main --posthoc --methods skill_ledger_robust` for each model and its runs (Amendment A1).",
                  "`analysis/audit_responses.py`, then the table and figure scripts.",
              ]},
              P("Re-running with the shipped response cache reproduces every number without API calls."),
              H1("Appendix B. Additional Results")]
    # B1: CIs
    rows = []
    for me in C.MAIN:
        lib = me != "no_skills"
        rows.append([C.LABEL[me]] + [r.ci(A, "overall", me, k) if (lib or k.startswith("task")) else "–"
                                     for k in ("retention", "repair", "retirement", "component_correct",
                                               "task_success", "task_policy_violation")])
    blocks.append({"type": "table", "caption": f"Main test-split results with 95% cluster-bootstrap intervals ({A}, "
                   "three runs; %).", "header": ["Method", "Retention", "Repair", "Retirement", "Correct",
                                                 "Task success", "Task viol."],
                   "widths": [2.5, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3], "rows": rows, "size": 15})
    # B2: dev split
    rows = []
    for me in C.MAIN + ["ledger_no_quarantine", "ledger_no_tombstones", "ledger_nonselective"]:
        if me not in r.m(A)["dev_overall"]:
            continue
        lib = me != "no_skills"
        lab = C.LABEL[me] if not me.startswith("ledger_") else "SkillLedger " + C.LABEL[me]
        rows.append([lab] + [r.pct(A, "dev_overall", me, k) if (lib or k.startswith("task")) else "–"
                             for k in ("retention", "repair", "retirement", "component_correct", "task_success",
                                       "task_policy_violation")] + [r.cost(A, "dev_overall", me)])
    blocks.append({"type": "table", "caption": f"Development-split results ({A}, three runs; %, cost in m$ per event). "
                   "SkillLedger was revised on these events (Section 5.4), so they are not a fair comparison and are "
                   "shown for completeness.",
                   "header": ["Method", "Retention", "Repair", "Retire.", "Correct", "Task succ.", "Task viol.",
                              "m$/event"],
                   "widths": [3.2, 1.1, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1], "rows": rows, "size": 16})
    # B3: per family components correct
    fc = r.m(A)["extras"]["family_correct"]
    fams = [f for f in S.FAM_ORDER if f in fc["skill_ledger"]]
    meths = ["static", "version_aware", "regenerate", "regression_gated", "regression_refresh", "skill_ledger"]
    rows = [[S.FAM_NAME[f]] + [f"{100 * fc[m][f]:.0f}" for m in meths] for f in fams]
    blocks.append({"type": "table", "caption": f"Share of components correct after adaptation per family ({A}, test "
                   "split, %). Families without test events are omitted.",
                   "header": ["Family", "Static", "Vers.-aware", "Regen.", "Gated", "Gated+refr.", "SkillLedger"],
                   "widths": [3.2, 0.9, 1.1, 0.9, 0.9, 1.1, 1.1], "rows": rows, "size": 16})
    # B4: losses by event
    lb = r.m(A)["extras"]["loss_by_event"]
    keys = sorted({k for m in ("regenerate", "version_aware", "regression_refresh", "skill_ledger") for k in lb[m]})
    rows = [[k.split("|")[0], S.FAM_NAME[k.split("|")[1]]] + [str(lb[m].get(k, 0)) for m in
                                                               ("version_aware", "regenerate", "regression_refresh",
                                                                "skill_ledger")] for k in keys]
    blocks.append({"type": "table", "caption": f"Accidental losses (component outcomes, three runs pooled) by test "
                   f"event ({A}). The regression gate without refresh lost none.",
                   "header": ["Event", "Family", "Vers.-aware", "Regen.", "Gated+refr.", "SkillLedger"],
                   "widths": [1.6, 3.0, 1.1, 0.9, 1.1, 1.1], "rows": rows, "size": 16, "leftcols": 2})
    blocks += [H1("Appendix C. Model-call stages"),
               {"type": "table", "caption": "Stages at which methods call the model. All prompts are stored verbatim "
                "with every response in the artifact.",
                "header": ["Stage", "Used by", "Receives", "Returns"],
                "widths": [1.4, 2.0, 3.6, 2.2], "size": 16, "leftcols": 4, "rows": [
                    ["ledger_setup", "SkillLedger (once per family)", "contract, code, tests, deployment context, policy "
                     "text", "JSON: grounds per component, evidence per test"],
                    ["impact", "SkillLedger (once per family and event)", "change document, current policy, ledger, test "
                     "results", "JSON: retain/repair/retire per component, valid/stale per test"],
                    ["repair", "SkillLedger", "decisions, retained evidence, failures, feedback", "module + new tests"],
                    ["regenerate", "Full regeneration", "contract, interface, documentation bundle", "module + tests"],
                    ["propose", "Both gates", "change document, code, test results", "candidate module (2 per skill)"],
                    ["refresh_tests", "Gate + refresh", "change document, current tests", "rewritten test module"],
                    ["task", "All methods", "task statement, library (and/or documentation, tombstones)",
                     "solution module"]]}]
    return blocks


REPO = "https://github.com/lakshmi-charan/skillshift"
RELEASE = REPO + "/releases/tag/v1.0"


def declarations():
    import os
    c = os.environ.get("SKILLSHIFT_COMMIT")   # set when building the manuscript: full hash of the v1.0 commit
    commit = f"commit {c}" if c else "the commit tagged v1.0"
    return [H1("Declarations"),
            P("**Funding.** This research was self-funded by the author and received no external funding."),
            P("**Author contributions.** Lakshmi Charan Lingisetty: conceptualization, methodology, software, "
              "investigation, validation, formal analysis, visualization, and writing (original draft, review and "
              "editing). The author reviewed and approved the final manuscript and accepts responsibility for its "
              "content."),
            P("**Data and code availability.** The SkillShift benchmark, SkillLedger implementation, baseline "
              f"methods, study protocol, recorded evaluation outcomes, and analysis scripts are publicly available at "
              f"{REPO}. The artifacts corresponding to this manuscript are archived in release v1.0 at {RELEASE}, "
              f"corresponding to {commit}. The release includes the raw-records archive, containing the "
              "recorded prompts, model responses, token usage, estimated costs, and timings for 12,612 model calls, "
              "together with skill-library snapshots after each recorded state. The evaluation records in the "
              "repository support regeneration of the reported numerical results, tables, and figures. The "
              "raw-records archive provides the underlying model interactions and generated code for inspection and "
              "reconstruction of the response cache. Third-party materials remain subject to their respective "
              "licenses and attribution requirements."),
            P("**Corresponding author.** Lakshmi Charan Lingisetty. Email: lingisettycharan123@gmail.com")]


def main():
    N = nums()
    r = C.Res(RES / "results.json", RUNS / "response_audit.json")
    r.R["_nums"] = N
    ledger = json.loads((RUNS / "cost_ledger.json").read_text())
    r.R["_total_spend"] = ledger["total_usd"]
    labels = json.loads((RUNS / "labels.json").read_text())
    fam_rows, _ = S.family_table(labels)
    ev_rows = S.event_table(labels)
    tag = "gpt-41-mini"
    figs = {"lib": str(RES / f"fig_lib_{tag}.png"), "stack": str(RES / f"fig_stack_{tag}.png"),
            "task": str(RES / f"fig_task_{tag}.png"), "cost": str(RES / f"fig_cost_{tag}.png"),
            "abl": str(RES / "fig_ablation.png")}
    for k in list(figs):
        figs[k + "_px"] = px(figs[k])
    intro = T.intro(N)
    blocks = [{"type": "abstract", "text": C.abstract(r)},
              {"type": "keywords", "text": "continual learning; LLM agents; skill libraries; tool evolution; policy "
                                           "compliance; machine unlearning; regression testing; software evolution; "
                                           "benchmark"}]
    blocks += intro + C.intro_findings(r)
    blocks += T.related() + T.formulation() + T.benchmark(N, fam_rows, ev_rows) + T.method() + T.setup(N)
    blocks += C.results(r, figs) + C.discussion(r) + C.threats(r) + C.conclusion(r) + declarations()
    blocks += [H1("References"), {"type": "refs", "items": S.REFS}]
    blocks += appendix(r, N)
    OUT.write_text(json.dumps({"meta": {"title": S.TITLE, "authors": S.AUTHORS, "creator": S.AUTHORS[0]},
                               "blocks": blocks}, ensure_ascii=False, indent=1))
    print("wrote", OUT, len(blocks), "blocks")


if __name__ == "__main__":
    main()
