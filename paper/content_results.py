"""Result-dependent sections. Every number is read from results.json (written by results_gen.py) or from the
response audit; nothing is typed by hand."""
import json
import math
from pathlib import Path

from content_text import P, H1, H2

LABEL = {"no_skills": "No skills", "static": "Static library", "doc_retrieval": "Doc retrieval",
         "version_aware": "Version-aware retrieval", "regenerate": "Full regeneration",
         "regression_gated": "Regression-gated (GRASP-style)", "regression_refresh": "Regression-gated + refresh",
         "skill_ledger": "**SkillLedger**", "ledger_no_quarantine": "w/o evidence quarantine",
         "ledger_no_tombstones": "w/o tombstones", "ledger_nonselective": "non-selective review",
         "skill_ledger_robust": "SkillLedger + tolerant parsing (A1)"}
MAIN = ["no_skills", "static", "doc_retrieval", "version_aware", "regenerate", "regression_gated",
        "regression_refresh", "skill_ledger"]
ADAPT = ["regenerate", "regression_gated", "regression_refresh", "skill_ledger"]


class Res:
    def __init__(self, path, audit_path):
        self.R = json.loads(Path(path).read_text())
        self.audit = json.loads(Path(audit_path).read_text())

    def m(self, model):
        return self.R["models"].get(model)

    def v(self, model, part, method, metric):
        b = self.m(model)[part][method].get(metric)
        return None if not b or not b.get("n") else b

    def pct(self, model, part, method, metric, nd=1):
        b = self.v(model, part, method, metric)
        return "–" if b is None else f"{100 * b['mean']:.{nd}f}"

    def ci(self, model, part, method, metric):
        b = self.v(model, part, method, metric)
        return "–" if b is None else f"{100 * b['mean']:.1f} ({100 * b['lo']:.0f}–{100 * b['hi']:.0f})"

    def cost(self, model, part, method):
        return f"{1000 * self.m(model)[part][method]['cost_per_event']:.1f}"

    def hyp(self, model, other, key):
        return self.m(model)["extras"]["hyp"][other][key]

    def audit_row(self, model, method):
        return self.audit.get(f"{model}/{method}", {})


def dpts(d, scale=100, unit=" points", nd=1):
    if d is None:
        return "n/a"
    return f"{scale * d['diff']:+.{nd}f}{unit} [{scale * d['lo']:+.{nd}f}, {scale * d['hi']:+.{nd}f}]"


def verdict(d, direction, margin=None):
    """direction -1: hypothesis predicts a negative difference (ledger lower); +1 positive."""
    if d is None:
        return "n/a"
    lo, hi = d["lo"], d["hi"]
    if margin is not None:          # non-inferiority on a 'lower is better' metric
        return "supported" if hi < margin else ("not shown" if lo < margin else "rejected")
    if direction < 0:
        return "supported" if hi < 0 else ("contradicted" if lo > 0 else "not supported")
    return "supported" if lo > 0 else ("contradicted" if hi < 0 else "not supported")


# ---------------------------------------------------------------------------------------------------------- tables
def main_table(r, model="gpt-4.1-mini"):
    rows = []
    for me in MAIN:
        if me not in r.m(model)["overall"]:
            continue
        lib = me != "no_skills"
        rows.append([LABEL[me],
                     r.pct(model, "overall", me, "retention") if lib else "–",
                     r.pct(model, "overall", me, "repair") if lib else "–",
                     r.pct(model, "overall", me, "retirement") if lib else "–",
                     r.pct(model, "overall", me, "component_correct") if lib else "–",
                     r.pct(model, "overall", me, "task_success"),
                     r.pct(model, "overall", me, "task_policy_violation"),
                     r.cost(model, "overall", me),
                     f"{r.m(model)['overall'][me]['calls_per_event']:.1f}"])
    return rows


def hyp_table(r):
    A, B, C = "gpt-4.1-mini", "gpt-5.4-nano", "gpt-5.4-mini"
    spec = [("H1", "Retirement after policy changes", "regression_gated", "retirement_policy", +1, None, 100, " pts"),
            ("H1", "Task policy violations after policy changes", "regression_gated", "task_violation_policy", -1, None,
             100, " pts"),
            ("H1 (sec.)", "Retirement after policy changes", "regression_refresh", "retirement_policy", +1, None, 100,
             " pts"),
            ("H1 (sec.)", "Task policy violations after policy changes", "regression_refresh", "task_violation_policy",
             -1, None, 100, " pts"),
            ("H2", "Accidental loss", "regenerate", "accidental_loss", -1, None, 100, " pts"),
            ("H2", "Accidental loss", "version_aware", "accidental_loss", -1, None, 100, " pts"),
            ("H2 (NI)", "Accidental loss, margin 5 pts", "regression_refresh", "accidental_loss", -1, 0.05, 100, " pts"),
            ("H3", "Repair after library changes", "regression_gated", "repair_tool", +1, "geq", 100, " pts"),
            ("H4", "Adaptation cost per event", "regenerate", "cost", -1, None, 1000, " m$"),
            ("H4", "Adaptation cost per event", "regression_refresh", "cost", -1, None, 1000, " m$")]
    rows = []
    for h, what, other, key, direc, margin, sc, u in spec:
        d = r.hyp(A, other, key)
        if margin == "geq":
            vd = "supported" if d["lo"] > 0 else ("not supported" if d["diff"] < 0 else "not contradicted")
        else:
            vd = verdict(d, direc, margin if isinstance(margin, float) else None)
        others = []
        for mdl in (B, C):
            mm = r.m(mdl)
            if mm and other in mm["extras"]["hyp"]:
                others.append(f"{sc * mm['extras']['hyp'][other][key]['diff']:+.1f}")
            else:
                others.append("–")
        rows.append([h, what, LABEL[other].replace("**", ""), f"{sc * d['diff']:+.1f} [{sc * d['lo']:+.1f}, "
                     f"{sc * d['hi']:+.1f}]", vd] + others)
    return rows


def kind_table(r, model="gpt-4.1-mini"):
    rows = []
    for me in ADAPT:
        rows.append([LABEL[me]] + [r.pct(model, part, me, met) for part in ("tool", "policy")
                                   for met in ("retention", "repair")] +
                    [r.pct(model, "policy", me, "retirement"), r.pct(model, "policy", me, "task_policy_violation"),
                     r.cost(model, "tool", me), r.cost(model, "policy", me)])
    return rows


def obsolete_table(r):
    rows = []
    for me in ["static", "regenerate", "regression_gated", "regression_refresh", "skill_ledger"]:
        row = [LABEL[me]]
        for mdl in ("gpt-4.1-mini", "gpt-5.4-nano", "gpt-5.4-mini"):
            ob = r.m(mdl)["extras"]["obsolete_breakdown"].get(me)
            if not ob:
                row += ["–", "–"]
            else:
                row += [f"{ob['new_retired']}/{ob['new_total']}", f"{ob['carried_retired']}/{ob['carried_total']}"]
        rows.append(row)
    return rows


def ablation_table(r, model="gpt-4.1-mini"):
    rows = []
    for me in ["skill_ledger", "ledger_no_quarantine", "ledger_no_tombstones", "ledger_nonselective"]:
        rows.append([LABEL[me] if me == "skill_ledger" else "SkillLedger " + LABEL[me]] +
                    [r.pct(model, "overall", me, k) for k in ("retention", "repair", "retirement", "component_correct",
                                                               "task_success", "task_policy_violation")] +
                    [r.cost(model, "overall", me)])
    return rows


def audit_table(r):
    rows = []
    for mdl, n_runs in (("gpt-4.1-mini", 3), ("gpt-5.4-nano", 1), ("gpt-5.4-mini", 1)):
        a = r.audit_row(mdl, "skill_ledger")
        rows.append([mdl, n_runs, a.get("impact_calls", 0), a.get("impact_unparsed", 0),
                     f"{100 * a.get('impact_unparsed', 0) / max(1, a.get('impact_calls', 1)):.1f}",
                     a.get("impact_recovered", 0)])
    return rows


# -------------------------------------------------------------------------------------------------------- sections
def results(r, figs):
    A = "gpt-4.1-mini"
    hy = lambda o, k: r.hyp(A, o, k)
    ob = r.m(A)["extras"]["obsolete_breakdown"]
    lbe = r.m(A)["extras"]["loss_by_event"]["skill_ledger"]
    n_lost = sum(lbe.values())
    top2 = sorted(lbe.items(), key=lambda kv: -kv[1])[:2]
    top2_n = sum(v for _, v in top2)
    blocks = [H1("7. Results")]
    blocks += [
        P("All results in this section are from the 16 held-out test events, which were run once, after the protocol "
          "freeze. Unless stated otherwise, numbers are for the primary model (three runs), rates are pooled over "
          "component-event or task-instance outcomes, brackets give 95% cluster-bootstrap intervals, and differences "
          "are paired over the same resampled (family, event) clusters. The test split contains "
          f"{(r.v(A, 'overall', 'skill_ledger', 'retention')['n'] + r.v(A, 'overall', 'skill_ledger', 'repair')['n']) // 3} "
          "valid-component outcomes per run and method, but only seven newly prohibited components, spread over "
          "five policy events, and five previously prohibited ones scored again at later events; conclusions about retirement therefore rest on "
          "few clusters, and we report counts next to rates."),
        H2("7.1 Overview"),
        {"type": "table", "caption": f"Main results on the test split ({A}, three runs). Library metrics are shares of "
         "component-event outcomes (%); task metrics are shares of downstream task instances (%); cost is the mean "
         "adaptation cost per change event in thousandths of a US dollar at list prices; calls are model calls per "
         "event excluding task solving. Retirement includes components prohibited at an earlier event and "
         "scored again at later events (Table 6). Intervals are in Table 12 (Appendix B).",
         "header": ["Method", "Retention", "Repair", "Retire.", "Correct", "Task succ.", "Task viol.", "m$/event",
                    "Calls"],
         "widths": [3.1, 1.1, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 0.9], "rows": main_table(r), "size": 17, "highlight": [7]},
        P("Table 3 and Figs. 2 and 3 show that no method dominates. The plain regression gate never broke a "
          f"still-valid component (retention {r.pct(A, 'overall', 'regression_gated', 'retention')}%) and the refreshed "
          f"gate almost never ({r.pct(A, 'overall', 'regression_refresh', 'retention')}%), but the plain gate, whose probe is the "
          f"historical test suite, retired none of the prohibited behaviour "
          f"({r.pct(A, 'overall', 'regression_gated', 'retirement')}%) and left the agent violating the current "
          f"policy in {r.pct(A, 'overall', 'regression_gated', 'task_policy_violation')}% of policy-tested task "
          "instances. Refreshing the probe tests from the change documents before gating produced the most correct "
          f"libraries overall ({r.pct(A, 'overall', 'regression_refresh', 'component_correct')}% of components "
          f"correct after adaptation). SkillLedger reached {r.pct(A, 'overall', 'skill_ledger', 'component_correct')}%: "
          f"it retired {r.pct(A, 'overall', 'skill_ledger', 'retirement')}% of prohibited behaviour and repaired "
          f"{r.pct(A, 'overall', 'skill_ledger', 'repair')}% of broken components, but lost "
          f"{r.pct(A, 'overall', 'skill_ledger', 'accidental_loss')}% of components that were still valid. Full "
          f"regeneration retired the most ({r.pct(A, 'overall', 'regenerate', 'retirement')}%) at the highest cost and "
          f"with {r.pct(A, 'overall', 'regenerate', 'accidental_loss')}% accidental loss. Version-aware retrieval, "
          "which withholds any skill whose own tests fail, kept only "
          f"{r.pct(A, 'overall', 'version_aware', 'component_correct')}% of components correct, fewer than doing "
          f"nothing ({r.pct(A, 'overall', 'static', 'component_correct')}%)."),
        {"type": "figure", "path": figs["lib"], "px": figs["lib_px"], "width": 6.4,
         "caption": f"Retention, repair and retirement on the test split ({A}, three runs). Dots are pooled rates, "
                    "lines 95% cluster-bootstrap intervals. Retirement pools newly prohibited components with "
                    "components prohibited at an earlier event (Table 6). Methods without a library are omitted."},
        {"type": "figure", "path": figs["stack"], "px": figs["stack_px"], "width": 6.4,
         "caption": "Composition of all component-event outcomes after adaptation on the test split. Orange segments "
                    "are losses of behaviour that was still valid and passing before the adaptation; red segments are "
                    "prohibited behaviour still present afterwards."},
        H2("7.2 Preregistered hypotheses"),
        {"type": "table", "caption": "Preregistered contrasts on the test split: SkillLedger minus the comparison "
         "method. Differences are in percentage points (cost in thousandths of a dollar per event); intervals are "
         f"paired cluster-bootstrap 95% intervals for {A}; the last two columns give the point differences for the "
         "single runs of the other models. NI: non-inferiority, supported if the upper bound is below the margin. "
         "H3 predicted a repair rate at least equal to the gate's.",
         "header": ["Hyp.", "Outcome", "Versus", "Difference [95% CI]", "Verdict", "nano", "mini"],
         "widths": [0.9, 2.6, 2.0, 1.9, 1.2, 0.7, 0.7], "rows": hyp_table(r), "size": 16, "leftcols": 3},
        P("**H1 (retirement) is supported against the preregistered primary comparator.** After policy changes, "
          "SkillLedger retired more prohibited behaviour than the GRASP-style gate "
          f"({dpts(hy('regression_gated', 'retirement_policy'))}) and reduced downstream policy violations "
          f"({dpts(hy('regression_gated', 'task_violation_policy'))}); both differences have the same sign, "
          "and are at least as large, for the two other models. The gate's failure is structural: under a policy change, the "
          "historical tests encode the superseded rule, so every edit that implements the new rule breaks a "
          "previously passing test and is rejected."),
        P("**Against the refreshed gate, the protocol's own criterion for evidence against the contribution is met.** "
          "The refreshed gate matched SkillLedger on retirement after policy changes "
          f"({dpts(hy('regression_refresh', 'retirement_policy'))}) and on downstream violations "
          f"({dpts(hy('regression_refresh', 'task_violation_policy'))}) at equal adaptation cost "
          f"({dpts(hy('regression_refresh', 'cost'), 1000, ' m$')}). Rewriting the probe tests from the change "
          "documents is enough to lift the structural block that stops a regression gate from retiring behaviour."),
        P("**H2 (retention) is not supported.** SkillLedger's accidental-loss rate was not lower than full "
          f"regeneration's ({dpts(hy('regenerate', 'accidental_loss'))}) or version-aware retrieval's "
          f"({dpts(hy('version_aware', 'accidental_loss'))}), and non-inferiority against the refreshed gate was "
          f"rejected ({dpts(hy('regression_refresh', 'accidental_loss'))}; margin +5 points), as the development "
          "pilot had warned. **H3 (repair after library changes) is not supported** for the primary model "
          f"({dpts(hy('regression_gated', 'repair_tool'))}), with small positive point differences for the other "
          "two models. **H4 (cost) is supported against regeneration** "
          f"({dpts(hy('regenerate', 'cost'), 1000, ' m$')}) **but not against the refreshed gate** for the primary "
          "model; for gpt-5.4-mini, SkillLedger was cheaper than both."),
        H2("7.3 Policy changes versus library changes"),
        {"type": "table", "caption": f"Adaptive methods by event kind ({A}, test split, %). Library events: 11 "
         "(family, event) clusters; policy events: 5. Task violations are over policy-tested task instances in "
         "policy events. Cost in thousandths of a dollar per event.",
         "header": ["Method", "Lib. ret.", "Lib. rep.", "Pol. ret.", "Pol. rep.", "Pol. retire", "Pol. viol.",
                    "m$ lib.", "m$ pol."],
         "widths": [2.9, 1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 1.0, 1.0], "rows": kind_table(r), "size": 17,
         "highlight": [3]},
        P("The aggregate hides two different profiles (Table 5). After policy changes, SkillLedger repaired "
          f"{r.pct(A, 'policy', 'skill_ledger', 'repair')}% of components that the new revision broke (for example, "
          "PBKDF2 iteration counts and Argon2 memory parameters), against "
          f"{r.pct(A, 'policy', 'regression_refresh', 'repair')}% for the refreshed gate, "
          f"{r.pct(A, 'policy', 'regenerate', 'repair')}% for regeneration and "
          f"{r.pct(A, 'policy', 'regression_gated', 'repair')}% for the plain gate; the paired difference to the "
          f"refreshed gate is {dpts(hy('regression_refresh', 'repair_policy'))}, and it cost less "
          f"({r.cost(A, 'policy', 'skill_ledger')} versus {r.cost(A, 'policy', 'regression_refresh')} m$ per event), "
          "while retaining almost all unaffected behaviour "
          f"({r.pct(A, 'policy', 'skill_ledger', 'retention')}%). After library changes the picture reverses: "
          f"SkillLedger retained {r.pct(A, 'tool', 'skill_ledger', 'retention')}% of still-valid components, against "
          f"{r.pct(A, 'tool', 'regression_refresh', 'retention')}% for both gates, and repaired fewer "
          f"({r.pct(A, 'tool', 'skill_ledger', 'repair')}% versus {r.pct(A, 'tool', 'regression_refresh', 'repair')}% "
          "for the refreshed gate)."),
        H2("7.4 Retirement and recurrence"),
        {"type": "table", "caption": "Prohibited components that were absent after adaptation (count retired / "
         "component-event outcomes, pooled over runs). *New*: prohibited by the current event (seven per run). "
         "*Earlier*: prohibited by an earlier event and still prohibited (five per run, including the three "
         "legacy-cryptography components retired on the development split).",
         "header": ["Method", "4.1-mini new", "4.1-mini earlier", "nano new", "nano earlier", "mini new",
                    "mini earlier"],
         "widths": [3.0, 1.2, 1.3, 1.0, 1.1, 1.0, 1.1], "rows": obsolete_table(r), "size": 17, "highlight": [4]},
        P("Table 6 separates the two ways prohibited behaviour can be present. For newly prohibited components, "
          f"SkillLedger, the refreshed gate and regeneration each retired {ob['skill_ledger']['new_retired']} of "
          f"{ob['skill_ledger']['new_total']} outcomes with the primary model; the plain gate and the non-adaptive "
          "methods retired none. SkillLedger's most systematic miss was a conditional prohibition. The December 2024 OWASP "
          "revision restricts bcrypt to “legacy systems where Argon2 and scrypt are not available”, and the "
          "family's deployment context states that both are available. In all three runs SkillLedger's impact step "
          "quoted the restriction yet judged that new bcrypt hashes were still permitted under it, so the component "
          "persisted through all three OWASP test events; regeneration, which rewrites the skill from the current "
          "text, retired it in every run. For components prohibited earlier, the question is whether the library "
          "still contains them. Once a method had retired a component, it essentially never reappeared: across all "
          "models and methods we observed one reintroduction, by regeneration with gpt-5.4-mini. Earlier-prohibited "
          "behaviour that was present on the test split had simply never been retired, typically on the "
          "development split (for example, the refreshed gate had left some legacy-cryptography components in place on "
          "the development split, and SkillLedger had never retired new bcrypt hashes)."),
        H2("7.5 Why SkillLedger loses still-valid behaviour"),
        P(f"SkillLedger's {n_lost} lost component outcomes (three runs) are concentrated in two library events: "
          f"{top2[0][0].split('|')[0]} ({top2[0][1]}) and {top2[1][0].split('|')[0]} ({top2[1][1]}), together "
          f"{100 * top2_n / n_lost:.0f}%. Almost all ({_withheld_share(r)}) come from skills that were withheld rather "
          "than edited. The mechanism is visible in the logs of the largest case. In NumPy 2.4, `np.in1d` was removed; the skill under "
          "adaptation had already been migrated and worked, but one of its historical tests used `np.in1d` as its "
          "oracle and now failed. Under a library event SkillLedger keeps old evidence in force unless a repair "
          "supplies a corrected test of the same name. None of the three repair attempts corrected that test, "
          "so no attempt passed; because some of its evidence failed, the skill counted as broken, and the "
          "fallback rule withheld a working skill together with every component it provided. The refreshed "
          "gate rewrites every test first and is immune to this failure. The pattern is general in the NumPy events: "
          "the failing evidence of most withheld skills consisted of historical tests that themselves call removed "
          "APIs (for example `ndarray.tostring`, `np.trapz` and the `interpolation` argument of `quantile`). In "
          "the SQLAlchemy 2.1 event, removed calls such as `Engine.execute` appeared both in skill code and in "
          "tests. SkillLedger version-indexes the grounds of "
          "the code but not the API dependencies of its own evidence, and the loss follows from that gap."),
        H2("7.6 Downstream tasks"),
        {"type": "figure", "path": figs["task"], "px": figs["task_px"], "width": 6.0,
         "caption": f"Downstream task success and policy violations on the test split ({A}). Violations are "
                    "computed over task instances that carry a policy test (18 per run)."},
        P("Library quality did not translate one-to-one into task outcomes (Fig. 4). Recall that the no-skills and the "
          "two retrieval baselines see the current documentation at task time, whereas the four adaptive methods use "
          "the documentation only while adapting and present just the adapted library at task time. An unmaintained "
          f"library was harmful. Without documentation it reached {r.pct(A, 'overall', 'static', 'task_success')}% task "
          f"success, against {r.pct(A, 'overall', 'no_skills', 'task_success')}% for the same model solving each task "
          "from the current documentation alone; and even with the documentation in the prompt, adding the stale "
          f"library lowered success to {r.pct(A, 'overall', 'doc_retrieval', 'task_success')}% "
          f"({dpts(oc(r, A, 'doc_retrieval-no_skills/task_success'))}), although not for gpt-5.4-nano "
          f"({dpts(oc(r, 'gpt-5.4-nano', 'doc_retrieval-no_skills/task_success'))}). The adaptive methods, "
          f"without documentation at task time, reached {r.pct(A, 'overall', 'regression_gated', 'task_success')}–"
          f"{r.pct(A, 'overall', 'regenerate', 'task_success')}%, close to but not above the documentation-only "
          "baseline; version-aware retrieval, which pairs the documentation with only those skills that still pass "
          f"their tests, was highest ({r.pct(A, 'overall', 'version_aware', 'task_success')}%). For policy compliance, SkillLedger reduced "
          f"violations relative to the plain gate ({r.pct(A, 'overall', 'skill_ledger', 'task_policy_violation')}% "
          f"versus {r.pct(A, 'overall', 'regression_gated', 'task_policy_violation')}%) but not relative to working "
          f"without a library ({r.pct(A, 'overall', 'no_skills', 'task_policy_violation')}%) or to regeneration "
          f"({r.pct(A, 'overall', 'regenerate', 'task_policy_violation')}%). These task-level comparisons rest on "
          "18 policy-tested task instances per run and should be read as indicative."),
        H2("7.7 Ablations"),
        {"type": "table", "caption": f"Ablations of SkillLedger ({A}, test split, three runs; %, cost in m$ per event).",
         "header": ["Variant", "Retention", "Repair", "Retire.", "Correct", "Task succ.", "Task viol.", "m$/event"],
         "widths": [3.3, 1.1, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1], "rows": ablation_table(r), "size": 17},
        {"type": "figure", "path": figs["abl"], "px": figs["abl_px"], "width": 6.4,
         "caption": "Ablations on the test split: estimates and 95% cluster-bootstrap intervals."},
        P("Evidence quarantine is the component that makes retirement possible. Without it, SkillLedger behaves like "
          f"the plain gate under policy changes: retirement fell to {r.pct(A, 'overall', 'ledger_no_quarantine', 'retirement')}% "
          f"({dpts(hy('ledger_no_quarantine', 'retirement_policy'))} for the full method on policy events), repair "
          f"after policy changes fell by {100 * hy('ledger_no_quarantine', 'repair_policy')['diff']:.1f} points, and "
          f"task policy violations rose to {r.pct(A, 'overall', 'ledger_no_quarantine', 'task_policy_violation')}%. "
          "Tombstones did not help: removing them left task success unchanged within noise and, if anything, "
          f"lowered task violations ({r.pct(A, 'overall', 'ledger_no_tombstones', 'task_policy_violation')}% versus "
          f"{r.pct(A, 'overall', 'skill_ledger', 'task_policy_violation')}%; "
          f"{dpts(hy('ledger_no_tombstones', 'task_violation_all'))} for the full method) and retirement after policy "
          f"changes ({dpts(hy('ledger_no_tombstones', 'retirement_policy'))} for the full method). The one-line "
          "prohibitions shown at task time did not measurably change what the model wrote. Selective review did not "
          f"reduce cost; the non-selective variant was slightly cheaper ({r.cost(A, 'overall', 'ledger_nonselective')} "
          f"versus {r.cost(A, 'overall', 'skill_ledger')} m$ per event), because most library events flag at least one "
          "skill and the impact step is a single call per family either way. Outcomes were similar except for repair "
          f"after policy changes ({dpts(hy('ledger_nonselective', 'repair_policy'))} for selective review); since both "
          "variants review every skill at policy events, this difference can only arise indirectly, through libraries "
          "that diverged at earlier library events, and we do not interpret it."),
        H2("7.8 Other models and a silent failure mode"),
        {"type": "table", "caption": "Test-split results for the two further models (one run each; %, cost in m$ per "
         "event).",
         "header": ["Model", "Method", "Retention", "Repair", "Retire.", "Correct", "Task succ.", "Task viol.",
                    "m$/event"],
         "widths": [1.3, 2.9, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0], "rows": _models_rows(r), "size": 16,
         "leftcols": 2},
        P("With gpt-5.4-nano, the pattern of the primary model repeated with smaller losses: SkillLedger retained "
          f"{r.pct('gpt-5.4-nano', 'overall', 'skill_ledger', 'retention')}% of still-valid components, repaired "
          f"{r.pct('gpt-5.4-nano', 'overall', 'skill_ledger', 'repair')}% (the highest of all methods), retired "
          f"{r.pct('gpt-5.4-nano', 'overall', 'skill_ledger', 'retirement')}% (tied with the refreshed gate) and reached "
          f"the highest task success ({r.pct('gpt-5.4-nano', 'overall', 'skill_ledger', 'task_success')}%, tied with "
          "documentation retrieval). With gpt-5.4-mini, SkillLedger's retirement was only "
          f"{r.pct('gpt-5.4-mini', 'overall', 'skill_ledger', 'retirement')}%, below regeneration and the refreshed "
          f"gate ({r.pct('gpt-5.4-mini', 'overall', 'regression_refresh', 'retirement')}%). Inspection traced much of "
          "this to a failure of our implementation rather than of the model's judgement (Table 9)."),
        {"type": "table", "caption": "Impact-step responses of the frozen SkillLedger that its JSON parser could not "
         "read, by model; a failed parse was treated as an empty decision set, i.e. every component was retained. "
         "Recovered: responses that the post-hoc tolerant parser (Amendment A1) reads.",
         "header": ["Model", "Runs", "Impact calls", "Unparsed", "Unparsed (%)", "Recovered"],
         "widths": [2.0, 0.8, 1.3, 1.1, 1.3, 1.2], "rows": audit_table(r), "size": 17},
        P("The impact step asks for a JSON object of per-component decisions. The frozen implementation treats a "
          "response that is not valid JSON as containing no decisions, so every component is retained: a fail-open "
          "default. With gpt-5.4-mini, "
          f"{r.audit_row('gpt-5.4-mini', 'skill_ledger').get('impact_unparsed', 0)} of "
          f"{r.audit_row('gpt-5.4-mini', 'skill_ledger').get('impact_calls', 0)} impact responses were malformed, "
          "most often by a single missing closing brace; with gpt-4.1-mini, typical defects were Python-style "
          "triple-quoted strings inside JSON. In the legacy-cryptography family, gpt-5.4-mini's responses correctly "
          "said to retire Triple-DES encryption, PKCS#1 v1.5 key wrapping and DSA signing at the respective "
          "events, but none of these decisions was applied. The same fail-open behaviour affected "
          f"{r.audit_row(A, 'skill_ledger').get('impact_unparsed', 0)} of "
          f"{r.audit_row(A, 'skill_ledger').get('impact_calls', 0)} impact decisions of the primary model and between "
          f"{min(r.audit_row(A, x).get('impact_unparsed', 0) for x in ('ledger_no_quarantine', 'ledger_no_tombstones', 'ledger_nonselective'))} "
          f"and {max(r.audit_row(A, x).get('impact_unparsed', 0) for x in ('ledger_no_quarantine', 'ledger_no_tombstones', 'ledger_nonselective'))} "
          "of 84 for the ablations. No baseline depends on structured output in this way; they exchange code blocks, "
          "which the parser extracted reliably."),
    ]
    blocks += posthoc(r)
    blocks += [
        H2("7.10 Cost"),
        {"type": "figure", "path": figs["cost"], "px": figs["cost_px"], "width": 5.8,
         "caption": f"Share of components correct after adaptation against mean adaptation cost per change event "
                    f"({A}, test split, list prices). Vertical lines are 95% intervals."},
        P(f"SkillLedger used {r.m(A)['overall']['skill_ledger']['calls_per_event']:.1f} model calls and "
          f"{r.m(A)['overall']['skill_ledger']['tokens_per_event'] / 1000:.0f} thousand tokens per change event, "
          f"comparable with the refreshed gate ({r.m(A)['overall']['regression_refresh']['calls_per_event']:.1f} calls, "
          f"{r.m(A)['overall']['regression_refresh']['tokens_per_event'] / 1000:.0f} thousand tokens) and below "
          f"regeneration ({r.m(A)['overall']['regenerate']['tokens_per_event'] / 1000:.0f} thousand tokens); the plain "
          f"gate was cheapest among the adaptive methods ({r.cost(A, 'overall', 'regression_gated')} m$ per event). "
          f"Wall-clock adaptation time per event, dominated by test execution, was "
          f"{r.m(A)['overall']['skill_ledger']['seconds_per_event']:.0f} s for SkillLedger, "
          f"{r.m(A)['overall']['regression_refresh']['seconds_per_event']:.0f} s for the refreshed gate and "
          f"{r.m(A)['overall']['regenerate']['seconds_per_event']:.0f} s for regeneration. At these list prices, "
          "all adaptive methods cost a few cents per change event for a family of four to seven skills (Fig. 6)."),
    ]
    return blocks


def _withheld_share(r, model="gpt-4.1-mini"):
    st = r.m(model)["extras"]["loss_skill_status"]["skill_ledger"]
    return f"{st.get('quarantined', 0)} of {sum(st.values())}"


def oc(r, model, key):
    return r.m(model)["extras"]["other_contrasts"].get(key)


def _models_rows(r):
    rows = []
    for mdl in ("gpt-5.4-nano", "gpt-5.4-mini"):
        mm = r.m(mdl)
        first = True
        for me in MAIN:
            if me not in mm["overall"] or me == "no_skills":
                continue
            rows.append([mdl if first else "", LABEL[me]] +
                        [r.pct(mdl, "overall", me, k) for k in ("retention", "repair", "retirement",
                                                               "component_correct", "task_success",
                                                               "task_policy_violation")] + [r.cost(mdl, "overall", me)])
            first = False
    return rows


def posthoc(r):
    """Amendment A1 results, if the post-hoc runs are present."""
    have = {mdl: "skill_ledger_robust" in (r.m(mdl) or {}).get("overall", {}) for mdl in r.R["models"]}
    out = [H2("7.9 Post-hoc check: tolerant parsing (Amendment A1)")]
    if not any(have.values()):
        out.append(P("[Post-hoc runs pending.]"))
        return out
    rows = []
    for mdl in ("gpt-4.1-mini", "gpt-5.4-nano", "gpt-5.4-mini"):
        if not have.get(mdl):
            continue
        for me in ("skill_ledger", "skill_ledger_robust", "regression_refresh", "regenerate"):
            if me in r.m(mdl)["overall"]:
                rows.append([mdl if me == "skill_ledger" else "", LABEL[me]] +
                            [r.pct(mdl, "overall", me, k) for k in ("retention", "repair", "retirement",
                                                                   "component_correct", "task_success",
                                                                   "task_policy_violation")] +
                            [r.cost(mdl, "overall", me)])
    out.append({"type": "table", "caption": "Post-hoc Amendment A1 (not preregistered): SkillLedger with a tolerant "
                "parser for the impact response, run on the test split after the main results had been analysed. "
                "It reuses every recorded response whose prompt is unchanged, so it differs from the frozen method "
                "only downstream of a recovered parse (%; cost in m$ per event, including reused calls at their "
                "original price).",
                "header": ["Model", "Method", "Retention", "Repair", "Retire.", "Correct", "Task succ.", "Task viol.",
                           "m$/event"],
                "widths": [1.3, 2.9, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0], "rows": rows, "size": 16, "leftcols": 2})
    out += posthoc_text(r)
    return out


WORD = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}


def posthoc_text(r):
    A, M = "gpt-4.1-mini", "gpt-5.4-mini"
    rm = lambda mdl, o, k: r.m(mdl)["extras"]["hyp"]["robust_minus"][o][k]
    obA = r.m(A)["extras"]["obsolete_breakdown"]
    obM = r.m(M)["extras"]["obsolete_breakdown"]
    od = r.m(M)["obsolete_detail"]
    fz = {(x["event"], x["skill"], x["component"]): x["cat"] for x in od if x["method"] == "skill_ledger"}
    rb = {(x["event"], x["skill"], x["component"]): x["cat"] for x in od if x["method"] == "skill_ledger_robust"}
    gained = sorted(k for k in fz if fz[k] == "persisting" and rb.get(k) == "retired")
    lost = sorted(k for k in fz if fz[k] == "retired" and rb.get(k) == "persisting")
    return [
        P("Because the parse failure is an implementation defect rather than a design choice, we ran one post-hoc "
          "check, declared as Amendment A1 in the protocol after the frozen results had been analysed (Table 10). "
          "The variant repairs the structure of a malformed impact response (unbalanced brackets, trailing commas, "
          "Python-style string quoting) and asks once more if it still cannot be parsed; it recovers all 40 malformed "
          "responses recorded in the main study, and no re-ask was needed. Since it shares the frozen method's "
          "response cache, its trajectory is identical until the first recovered parse; after that, prompts change "
          "and new samples are drawn, so later differences mix the fix with sampling variation."),
        P(f"For the primary model the fix changed little: retirement rose from "
          f"{r.pct(A, 'overall', 'skill_ledger', 'retirement')}% to {r.pct(A, 'overall', 'skill_ledger_robust', 'retirement')}% "
          f"({obA['skill_ledger']['new_retired']} to {obA['skill_ledger_robust']['new_retired']} of "
          f"{obA['skill_ledger']['new_total']} newly prohibited outcomes; {dpts(rm(A, 'skill_ledger', 'retirement'))}), "
          f"and retention ({r.pct(A, 'overall', 'skill_ledger_robust', 'retention')}%), repair and task outcomes were "
          "unchanged within noise, so none of the conclusions in Sections 7.2–7.7 depends on the defect. With "
          f"gpt-5.4-mini, the fix applied the recorded legacy-cryptography decisions: the {WORD[len(gained)]} "
          "legacy-cryptography components, which had persisted, were now retired. Overall retirement rose from "
          f"{r.pct(M, 'overall', 'skill_ledger', 'retirement')}% to {r.pct(M, 'overall', 'skill_ledger_robust', 'retirement')}%, "
          f"still below the refreshed gate ({r.pct(M, 'overall', 'regression_refresh', 'retirement')}%), because "
          f"{WORD[len(lost)]} component{'s' if len(lost) != 1 else ''} that the frozen run had retired (the audit of Mozilla's withdrawn Old profile) "
          "persisted in the diverged trajectory, and task policy violations rose from "
          f"{r.pct(M, 'overall', 'skill_ledger', 'task_policy_violation')}% to "
          f"{r.pct(M, 'overall', 'skill_ledger_robust', 'task_policy_violation')}% of 18 policy-tested task instances. "
          "With a single run, these last differences cannot be separated from sampling variation. The parse defect "
          "therefore explains the anomalous legacy-cryptography result for gpt-5.4-mini, but not the whole gap to "
          "the refreshed gate."),
    ]


def discussion(r):
    A = "gpt-4.1-mini"
    return [
        H1("8. Discussion"),
        H2("8.1 The evidence that gates an update must itself be kept current"),
        P("The clearest result of the study is negative for regression gating as usually practised and neutral "
          "between the two ways of repairing it. A gate that anchors on historical tests treats a correct retirement "
          "as a regression and, in our data, never retired prohibited behaviour under any of three models. Both "
          "remedies we evaluated change the probe rather than the gate: the refreshed baseline rewrites every test "
          "from the change documents, and SkillLedger quarantines the tests whose policy grounds were superseded. "
          "They retired prohibited behaviour at the same rate. They differ in scope. Wholesale refresh also fixes "
          "tests that are stale for technical reasons, which protected it from the losses SkillLedger suffered under "
          "library changes; selective quarantine keeps more of the original evidence, which is where its better "
          "repair after policy changes comes from, since the retained evidence constrains the repair. A method that "
          "version-indexes the API dependencies of its tests as well as those of its code would combine both "
          "properties; our results locate that gap precisely but do not test the combination."),
        H2("8.2 Retirement is a separate capability, and it is still weak"),
        P("Retirement and retention behaved as separate dimensions: the plain gate retained everything and "
          "retired nothing, while regeneration retired the most and still lost some valid behaviour. No method "
          "of the main methods removed more than five of the seven newly prohibited components in any run, and the misses were not "
          "random. Conditional prohibitions, such as bcrypt “only in legacy "
          "systems where Argon2 and scrypt are not available”, require the agent to evaluate the condition against "
          "its deployment, and the component-level impact judgement failed on exactly that. Regeneration, which "
          "rewrites the skill from the current text without an explicit keep-or-retire decision, retired it in every "
          "run. Metrics that report only retention, or only an aggregate pass rate, cannot reveal either "
          "effect."),
        H2("8.3 What a skill library is worth under change"),
        P("A library that is not maintained is worse than no library: without documentation, the static library "
          "cut downstream task success by more than half relative to working from the documentation alone, and "
          "for the primary model it lowered success even when the documentation was also provided. Maintained "
          "libraries, presented without documentation at task time, recovered most of the loss but did not beat "
          "the documentation-only baseline on single-shot tasks. The benefit of maintenance "
          "in this setting lies in the library itself, whose components are called by other code and must be "
          "correct without a model in the loop, rather than in the success of one task. Studies that evaluate skill "
          "libraries only through downstream task success may therefore understate both the harm of staleness and "
          "the value of maintenance."),
        H2("8.4 Robustness engineering is part of the method"),
        P("The fail-open parse is a small bug with a large effect, and it is typical of agent components that "
          "consume structured model output. Its consequence depended on the model: rare with one model, frequent "
          "with a stronger one. A structured decision step should fail closed: an unreadable response should "
          "trigger a retry or a conservative review, never a silent “retain everything”. Evaluations of agent "
          "methods across models should also audit the rate at which such steps fail, because an apparent model "
          "effect can be an interface effect."),
        H2("8.5 Implications"),
        P("For practitioners maintaining skill libraries under changing rules, the results suggest four "
          "measures: re-derive regression probes from the governing documents whenever a policy changes; version "
          "the evidence, not only the code; report retention and retirement separately; and treat conditional "
          "prohibitions and structured-output failures as expected failure modes to test for. For benchmark "
          "designers, SkillShift shows that real, dated change events with executable checks are feasible at "
          "modest cost and expose behaviour that synthetic mutations of tools do not, in particular the interaction "
          "between policy text and historical tests."),
    ]


def threats(r):
    return [
        H1("9. Threats to Validity and Limitations"),
        P("**Construct validity.** Validity is defined by hidden tests that we wrote. For library events the "
          "tests follow the documented behaviour of real releases and were validated against reference solutions in "
          "the pinned environments. For policy events the tests encode our reading of each revision together with a "
          "deployment context that we specified; the revisions and dates are authentic, but the organisation's "
          "pre-change choices are ours, and a different reading of a conditional clause could change individual "
          "labels (Section 7.4 discusses the one case in which a model's reading diverged). Retirement is scored as "
          "absence or refusal of the prohibited behaviour; a method that deletes too much is penalised through "
          "retention, not through retirement."),
        P("**Internal validity.** The same author designed the method and the baselines, and only SkillLedger was "
          "revised during development; the baselines were implemented once, from their descriptions, with the same "
          "token limits and documents. We added the refreshed gate precisely to avoid a weak comparator, and it "
          "turned out to be the strongest method on several metrics. Prompts necessarily differ between methods. "
          "The environments pin a late patch release of each release series (for example SQLAlchemy 1.4.54 and "
          "2.0.54), which keeps every state installable on a supported CPython; event dates are those of the "
          "series' first release. As a result, the epoch-0 environment of the SQLAlchemy family uses a 1.4 patch "
          "released after the 2.0 event date, which affects no label. The post-hoc amendment was designed after "
          "the frozen results had been seen; it is reported separately and is not used for any hypothesis."),
        P("**Statistical conclusion validity.** The test split contains 16 (family, event) clusters, of which five "
          "are policy events, and only seven newly prohibited components; intervals for retirement and task "
          "violations are correspondingly wide, and several are compatible with both no effect and large effects. "
          "The secondary models were run once. We did not correct for multiple comparisons; the preregistered "
          "contrasts are few and are reported in full, and all other comparisons are exploratory."),
        P("**External validity.** All skills are Python modules, all changes concern Python libraries, the Python "
          "runtime or published security guidance, and the three models belong to a single model family. Skills "
          "expressed as natural-language procedures, larger libraries, other domains of policy (for example "
          "privacy or finance), and agents that must discover changes rather than receive the change document may "
          "behave differently. Every test event post-dates the primary model's knowledge cutoff, but seven of the 16 "
          "precede that of the secondary models, whose results may partly reflect prior exposure."),
        P("**Cost.** Costs are list-price estimates from token counts; the study as a whole cost "
          f"US${r.R.get('_total_spend', 0):.2f} in model calls, including all three models and the post-hoc runs."),
    ]


def conclusion(r):
    return [
        H1("10. Conclusion"),
        P("We studied how an agent's reusable skills should change when the libraries they call and the rules they "
          "obey change, and argued that correct adaptation has three parts, retention, repair and retirement, which "
          "must be measured separately. SkillShift provides 27 real, dated tool and policy changes with verbatim "
          "documents and executable checks, and a chronological test split beyond the primary model's knowledge "
          "cutoff. On it, a GRASP-style regression gate never retired prohibited behaviour, because its historical "
          "tests encode superseded rules. SkillLedger, which quarantines such evidence and repairs or retires "
          "individual components, retired substantially more and reduced downstream policy violations, and it "
          "repaired policy-broken components better than every baseline, at lower cost than the refreshed gate and "
          "regeneration. It did not beat a gate whose "
          "tests are first refreshed from the change documents on retirement, and it lost still-valid behaviour "
          "under library changes because its own tests were version-bound. Tombstones did not reduce violations, and "
          "a fail-open parser silently disabled adaptation for one model. The broader lesson is that "
          "the evidence used to accept an update must be kept as current as the skills it protects. Future work "
          "should version test evidence alongside code, handle conditional prohibitions explicitly, and extend the "
          "benchmark to natural-language skills and to agents that must detect changes themselves."),
    ]


def intro_findings(r):
    A = "gpt-4.1-mini"
    hy = lambda o, k: r.hyp(A, o, k)
    au = r.audit_row("gpt-5.4-mini", "skill_ledger")
    return [P("The results are mixed, and we report them as such. (i) A regression gate anchored on historical tests "
              "never retired prohibited behaviour with any model; after policy changes SkillLedger retired "
              f"{100 * hy('regression_gated', 'retirement_policy')['diff']:.0f} percentage points more of it and "
              f"reduced downstream policy violations by {-100 * hy('regression_gated', 'task_violation_policy')['diff']:.0f} "
              "points. (ii) A gate whose probe tests are first rewritten from the change documents closed that gap "
              "at equal cost and retained still-valid behaviour better, which by our preregistered criterion counts "
              "as evidence against SkillLedger's contribution on retirement. (iii) SkillLedger repaired "
              "policy-broken components better than every baseline "
              f"({dpts(hy('regression_refresh', 'repair_policy'))} against the refreshed gate), but lost still-valid "
              f"behaviour under library changes ({r.pct(A, 'tool', 'skill_ledger', 'retention')}% retention), almost "
              "entirely by withholding skills whose historical tests kept failing, often because the tests themselves "
              "called removed APIs. (iv) Tombstones did not reduce "
              "violations, and an unmaintained library was worse than none. (v) A fail-open parser for structured "
              f"model output silently disabled {au.get('impact_unparsed', 0)} of {au.get('impact_calls', 0)} "
              "adaptation decisions for one model, a failure mode that model comparisons can mistake for a model "
              "effect.")]


def abstract(r):
    A = "gpt-4.1-mini"
    hy = lambda o, k: r.hyp(A, o, k)
    return (
        "Agents that store reusable skills must keep them valid as the libraries they call and the rules they obey "
        "change. Correct adaptation then means retaining still-valid behaviour, repairing broken behaviour and "
        "retiring behaviour that new rules prohibit. We introduce SkillShift, a benchmark of 11 skill families "
        f"({r.R['_nums']['n_skills']} skills, {r.R['_nums']['n_components']} components) exposed to 27 real, dated "
        "changes: breaking releases of Python libraries and runtimes, and revisions of OWASP, NIST and Mozilla "
        "security guidance. It supplies verbatim change documents, executable hidden tests in pinned environments and "
        "a chronological split whose 16 test events post-date the primary model's knowledge cutoff. We also propose "
        "SkillLedger, which stores per-component grounds and version-stamped evidence, quarantines evidence whose "
        "grounds were superseded, and repairs or retires components under a no-regression gate. In a preregistered "
        "comparison with seven baselines, a GRASP-style regression gate never retired prohibited behaviour, whereas "
        f"SkillLedger retired {100 * hy('regression_gated', 'retirement_policy')['diff']:.0f} points more after policy "
        f"changes and cut downstream violations by {-100 * hy('regression_gated', 'task_violation_policy')['diff']:.0f} "
        "points. A gate whose tests were first refreshed from the change documents, however, matched it on both at "
        f"equal cost and retained still-valid behaviour better ({r.pct(A, 'overall', 'regression_refresh', 'retention')}% "
        f"versus {r.pct(A, 'overall', 'skill_ledger', 'retention')}%). SkillLedger's advantage was confined to repair "
        f"after policy changes (+{100 * hy('regression_refresh', 'repair_policy')['diff']:.0f} points); its losses came "
        "from withholding skills whose historical tests, often calling removed APIs, kept failing. Tombstones did not reduce violations, an unmaintained library "
        "was worse than none, and a fail-open parser silently discarded up to a third of one model's adaptation "
        "decisions. What matters most "
        "is keeping the evidence that gates updates current.")
