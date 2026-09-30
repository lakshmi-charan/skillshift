"""Adaptation methods compared in the study.

Every method starts from the same epoch-0 library and sees the same change documentation. They differ in
what they keep and how they update it:

  no_skills           no library; tasks are solved from the current documentation
  static              epoch-0 library, never updated, no documentation
  doc_retrieval       epoch-0 library + current documentation retrieved at task time
  version_aware       library entries re-validated by executing their tests in each new runtime; entries whose
                      tests fail are withheld from retrieval; current documentation at task time
  regenerate          every skill of the affected family is rewritten from its specification + current docs
  regression_gated    GRASP-style gate: candidate edits are accepted only if they fix previously failing tests
                      without breaking previously passing ones (historical tests are the probe set)
  regression_refresh  regression gate after an LLM refresh of every test file against the change docs
  skill_ledger        (proposed) version-indexed evidence: grounds per component, quarantine of evidence whose
                      grounds changed, per-component retain/repair/retire, tombstones for retired behaviour

Post-hoc amendment A1 (added after the frozen test run; see PROTOCOL.md):
  skill_ledger_robust skill_ledger with a structurally tolerant parser for the impact response and one re-ask when
                      it still cannot be parsed. It shares skill_ledger's response cache, so every call whose prompt
                      is unchanged returns the identical recorded response; only the parse step differs.
"""
import copy

from . import bench, prompts
from .library import (run_agent_tests, summarize_results, passed_set, failed_set, api_dependencies,
                      mentioned_in, extract_blocks, extract_json, extract_json_tolerant, compiles, code_map)


class Ctx:
    """Per (model, method, run) context: LLM access with accounting and logging."""

    def __init__(self, model, method, run, log_path, chat_fn):
        self.model, self.method, self.run, self.log_path, self._chat = model, method, run, log_path, chat_fn
        self.cache_method = method   # name used in the cache salt (a variant may share its parent's cache)
        self.usage = []

    def chat(self, system, user, stage, family, state, skill=None, attempt=0, max_tokens=10000, share_key=None):
        meta = {"method": self.method, "run": self.run, "family": family, "state": state, "stage": stage,
                "skill": skill, "attempt": attempt}
        salt = {"run": self.run, "k": share_key or [self.cache_method, stage, family, state, skill, attempt]}
        r = self._chat(self.model, [{"role": "user", "content": user}], system=system, stage=stage, salt=salt,
                       log_path=self.log_path, meta=meta, max_tokens=max_tokens)
        self.usage.append({**meta, "input_tokens": r["usage"].get("input_tokens", 0),
                           "output_tokens": r["usage"].get("output_tokens", 0), "cost": r["cost"],
                           "latency_s": r["latency_s"], "cached": r.get("cached", False),
                           "finish_reason": r.get("finish_reason")})
        return r["text"]


def _hist(rec, sid, action, detail=""):
    rec["history"].append({"state": sid, "action": action, "detail": detail})


# ============================================================================= non-adaptive
class Method:
    name = "base"
    adaptive = False
    uses_library = True

    def init(self, fid, lib, ctx):
        return {"lib": copy.deepcopy(lib), "tombstones": []}

    def adapt(self, fid, sid, ms, ctx):
        return ms

    def task_context(self, fid, sid, ms):
        skills = [r for r in ms["lib"].values() if r["status"] == "active"]
        return {"skills": skills, "tombstones": None, "docs": None}


class NoSkills(Method):
    name = "no_skills"
    uses_library = False

    def task_context(self, fid, sid, ms):
        return {"skills": None, "tombstones": None, "docs": prompts.docs_bundle(fid, sid)}


class Static(Method):
    name = "static"


class DocRetrieval(Method):
    name = "doc_retrieval"

    def task_context(self, fid, sid, ms):
        c = super().task_context(fid, sid, ms)
        c["docs"] = prompts.docs_bundle(fid, sid)
        return c


class VersionAware(Method):
    """Execution-based re-validation: an entry stays retrievable in a new runtime only if its tests pass there."""
    name = "version_aware"
    adaptive = True

    def adapt(self, fid, sid, ms, ctx):
        lib = ms["lib"]
        for kid, rec in lib.items():
            if rec["status"] == "retired":
                continue
            res = run_agent_tests(fid, sid, {**lib, kid: {**rec, "status": "active"}}, kid)
            ok = res.get("cases") and not res.get("import_error") and not failed_set(res)
            new = "active" if ok else "quarantined"
            if new != rec["status"]:
                _hist(rec, sid, "revalidated" if ok else "withheld", summarize_results(res, 3))
            rec["status"] = new
        return ms

    def task_context(self, fid, sid, ms):
        c = super().task_context(fid, sid, ms)
        c["docs"] = prompts.docs_bundle(fid, sid)
        return c


# ============================================================================= regeneration
class Regenerate(Method):
    name = "regenerate"
    adaptive = True
    max_attempts = 2

    def adapt(self, fid, sid, ms, ctx):
        lib = ms["lib"]
        for kid, rec in lib.items():
            if rec["status"] == "retired":
                continue
            feedback, best = None, None
            for attempt in range(self.max_attempts):
                txt = ctx.chat(prompts.REGEN_SYSTEM, prompts.regen_prompt(fid, sid, rec, feedback), "regenerate",
                               fid, sid, kid, attempt)
                if txt.strip().splitlines() and txt.strip().splitlines()[0].strip().upper().startswith("RETIRED") \
                        and "```" not in txt:
                    best = ("retire", None, None)
                    break
                b = extract_blocks(txt)
                code = b.get("MODULE") or (b["_blocks"][0] if b["_blocks"] else None)
                tests = b.get("NEW TESTS") or (b["_blocks"][1] if len(b["_blocks"]) > 1 else "")
                if not code or not compiles(code):
                    feedback = "The module did not compile or was missing."
                    continue
                res = run_agent_tests(fid, sid, lib, kid, code=code, tests=tests)
                best = ("code", code, tests)
                if res.get("cases") and not failed_set(res) and not res.get("import_error"):
                    break
                feedback = summarize_results(res)
            if best is None:
                _hist(rec, sid, "regeneration_failed")
                continue
            if best[0] == "retire":
                rec["status"], rec["code"] = "retired", None
                _hist(rec, sid, "retired")
            else:
                rec["code"], rec["tests"], rec["status"] = best[1], best[2] or rec["tests"], "active"
                _hist(rec, sid, "regenerated")
        return ms


# ============================================================================= regression gate (GRASP-style)
class RegressionGated(Method):
    """Candidate edits are proposed from failures and the change documents; a candidate is accepted only if it
    produces a net improvement on the probe set (the skill's tests) with no new regressions:
    accept iff (F - R) > 0 and R <= R0 (R0 = 0), choosing the best F - R (Moll et al., 2026)."""
    name = "regression_gated"
    adaptive = True
    k_candidates = 2
    refresh = False

    def _probe(self, fid, sid, ms, ctx, kid):
        return ms["lib"][kid]["tests"]

    def adapt(self, fid, sid, ms, ctx):
        lib = ms["lib"]
        policy_event = bench.state(fid, sid)["event"]["kind"] == "policy"
        for kid, rec in lib.items():
            if rec["status"] == "retired":
                continue
            probe = self._probe(fid, sid, ms, ctx, kid)
            base = run_agent_tests(fid, sid, lib, kid, tests=probe)
            fail0, pass0 = failed_set(base), passed_set(base)
            if base.get("import_error"):
                fail0 |= pass0
                pass0 = set()
            if not fail0 and not policy_event:
                continue                               # nothing to fix: no proposals
            best, best_score = None, 0
            for v in range(self.k_candidates):
                txt = ctx.chat(prompts.PROPOSE_SYSTEM,
                               prompts.propose_prompt(fid, sid, {**rec, "tests": probe}, summarize_results(base), v + 1),
                               "propose", fid, sid, kid, v)
                b = extract_blocks(txt)
                code = b.get("MODULE") or (b["_blocks"][0] if b["_blocks"] else None)
                if not code or not compiles(code):
                    continue
                res = run_agent_tests(fid, sid, lib, kid, code=code, tests=probe)
                pc, fc = passed_set(res), failed_set(res)
                if res.get("import_error"):
                    fc |= pc
                    pc = set()
                F, R = len(fail0 & pc), len(pass0 & fc)
                if R <= 0 and (F - R) > best_score:
                    best, best_score = code, F - R
            if best is not None:
                rec["code"] = best
                _hist(rec, sid, "edit_accepted", f"net={best_score}")
            else:
                _hist(rec, sid, "no_edit_accepted")
            if self.refresh:
                rec["tests"] = probe
        return ms


class RegressionRefresh(RegressionGated):
    """Regression gate whose probe tests are first rewritten against the change documents (every test file,
    every event: non-selective)."""
    name = "regression_refresh"
    refresh = True

    def _probe(self, fid, sid, ms, ctx, kid):
        rec = ms["lib"][kid]
        txt = ctx.chat(prompts.REFRESH_SYSTEM, prompts.refresh_prompt(fid, sid, rec), "refresh_tests", fid, sid, kid)
        b = extract_blocks(txt)
        t = b.get("TESTS") or (b["_blocks"][0] if b["_blocks"] else None)
        if t and compiles(t) and "@case" in t:
            return t
        return rec["tests"]


# ============================================================================= SkillLedger (proposed)
class SkillLedger(Method):
    """Version-indexed evidence for selective retention, repair and retirement.

    Ledger (per skill): grounds per component (APIs + verbatim policy quotes), evidence per test (component,
    grounds), and the runtime/policy version under which everything was last validated.
    On a change: (1) execute the evidence in the new runtime; (2) if the change could touch the skill (a policy
    change, a failing test, or an API dependency named in the change document), classify every component as
    retain/repair/retire and every test as valid/stale in one call per family; (3) quarantine stale evidence,
    (4) repair or retire only affected components, gated on the remaining valid evidence plus new evidence;
    (5) write tombstones for retired behaviour so it is not reintroduced at task time."""
    name = "skill_ledger"
    adaptive = True
    max_attempts = 3
    use_quarantine = True
    use_tombstones = True
    selective = True

    def init(self, fid, lib, ctx):
        ms = super().init(fid, lib, ctx)
        s0 = bench.family(fid)["states"][0]["id"]
        txt = ctx.chat(prompts.LEDGER_SYSTEM, prompts.ledger_setup_prompt(fid, s0, ms["lib"]), "ledger_setup", fid,
                       s0, max_tokens=8000)
        data = extract_json(txt) or {}
        led = {}
        for kid, rec in ms["lib"].items():
            d = (data.get("skills") or {}).get(kid, {})
            led[kid] = {"components": d.get("components", {}), "tests": d.get("tests", {}),
                        "apis": api_dependencies(rec["code"]),
                        "validated_under": f"{s0}: {prompts.env_text(fid, s0)}"}
        ms["ledger"] = led
        ms["quarantined_tests"] = {}
        return ms

    # -- helpers
    @staticmethod
    def _split_tests(src, stale):
        """Remove stale test functions (by name) from a test module source; returns (kept_src, removed_names)."""
        import ast
        if not stale:
            return src, []
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return src, []
        lines = src.splitlines()
        drop = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in stale:
                start = min([d.lineno for d in node.decorator_list] + [node.lineno]) - 1
                drop.append((start, node.end_lineno))
        keep = [l for i, l in enumerate(lines) if not any(a <= i < b for a, b in drop)]
        return "\n".join(keep) + "\n", [n for n in stale]

    def _needs_review(self, fid, sid, rec, led, res, doc):
        if bench.state(fid, sid)["event"]["kind"] != "tool" or not self.selective:
            return True
        if res.get("import_error") or res.get("fatal") or failed_set(res):
            return True
        return bool(mentioned_in(led.get("apis", []), doc))

    def adapt(self, fid, sid, ms, ctx):
        lib, ledger = ms["lib"], ms["ledger"]
        kind = bench.state(fid, sid)["event"]["kind"]
        doc = prompts.event_doc(fid, sid)
        results, review = {}, []
        for kid, rec in lib.items():
            if rec["status"] == "retired":
                continue
            results[kid] = run_agent_tests(fid, sid, lib, kid)
            if self._needs_review(fid, sid, rec, ledger.get(kid, {}), results[kid], doc):
                review.append(kid)
        stamp = f"{sid}: {prompts.env_text(fid, sid)}"
        if not review:
            for kid in results:
                ledger[kid]["validated_under"] = stamp
            return ms
        sub = {k: lib[k] for k in review}
        impact = self._impact(fid, sid, sub, ledger, results, ctx)
        for kid in review:
            rec, led = lib[kid], ledger[kid]
            imp = impact.get(kid, {})
            decisions = {c: dict(d) for c, d in (imp.get("components") or {}).items() if isinstance(d, dict)}
            if kind == "tool":
                # a library change can break code but never makes behaviour unauthorised: retire -> repair
                for d in decisions.values():
                    if str(d.get("decision", "")).lower() == "retire":
                        d["decision"] = "repair"
            stale = {t for t, v in (imp.get("tests") or {}).items() if str(v).lower().startswith("stale")}
            if not self.use_quarantine:
                stale = set()
            kinds = {c["id"]: str(decisions.get(c["id"], {}).get("decision", "retain")).lower()
                     for c in rec["components"]}
            res = results[kid]
            broken = bool(res.get("import_error") or res.get("fatal") or (kind == "tool" and failed_set(res)))
            if all(v == "retain" for v in kinds.values()) and not broken and not (stale and kind == "policy"):
                led["validated_under"] = stamp
                continue
            if kind == "policy" and all(v == "retire" for v in kinds.values()):
                self._retire_skill(fid, sid, ms, kid, decisions)
                continue
            self._repair(fid, sid, ms, ctx, kid, decisions, stale, res, stamp, broken, kind)
        return ms

    def _impact(self, fid, sid, sub, ledger, results, ctx):
        txt = ctx.chat(prompts.IMPACT_SYSTEM, prompts.impact_prompt(fid, sid, sub, ledger, results), "impact", fid,
                       sid, max_tokens=8000)
        return (extract_json(txt) or {}).get("skills", {})

    def _tombstones_for(self, fid, sid, kid, decisions):
        st = bench.state(fid, sid)
        out = []
        for comp, d in decisions.items():
            if str(d.get("decision", "")).lower() == "retire":
                text = d.get("prohibition") or d.get("reason") or f"{kid}.{comp} is retired"
                out.append({"skill": kid, "component": comp, "text": f"{kid}/{comp}: {text}",
                            "source": (d.get("source") or st["event"].get("source", ""))[:300], "date": st["date"]})
        return out

    def _retire_skill(self, fid, sid, ms, kid, decisions):
        rec = ms["lib"][kid]
        rec["status"], rec["code"] = "retired", None
        _hist(rec, sid, "retired", "all components retired")
        if self.use_tombstones:
            ms["tombstones"].extend(self._tombstones_for(fid, sid, kid, decisions))

    @staticmethod
    def _test_names(src):
        import ast
        try:
            return {n.name for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}
        except SyntaxError:
            return set()

    def _accept(self, fid, sid, ms, kid, code, tests, decisions, stamp, note, removed=(), rule=None):
        rec = ms["lib"][kid]
        rec["code"], rec["tests"], rec["status"] = code, tests, "active"
        ms["ledger"][kid]["apis"] = api_dependencies(code)
        ms["ledger"][kid]["validated_under"] = stamp
        if removed:
            ms["quarantined_tests"].setdefault(kid, []).append({"state": sid, "tests": sorted(removed), "rule": rule})
        _hist(rec, sid, "repaired", note)
        if self.use_tombstones:
            ms["tombstones"].extend(self._tombstones_for(fid, sid, kid, decisions))

    def _repair(self, fid, sid, ms, ctx, kid, decisions, stale, res, stamp, broken, kind):
        """Evidence rules. Under a policy change, stale tests encode a superseded requirement and are quarantined
        (replaced by new evidence written from the new text). Under a tool change, old tests stay valid unless the
        repair supplies a corrected test with the same name (documented change of result). The repair must pass
        all remaining old evidence; new, unconfirmed tests that fail on the final attempt are dropped (recorded)."""
        lib, rec = ms["lib"], ms["lib"][kid]
        failing_txt = summarize_results(res)
        feedback = None
        policy_stale = stale if kind == "policy" else set()
        base_src0, _ = self._split_tests(rec["tests"], policy_stale)
        base_res = run_agent_tests(fid, sid, lib, kid, tests=base_src0)
        base_pass = set() if base_res.get("import_error") else passed_set(base_res)
        best = None   # (n_old_pass, n_new_pass, code, tests, removed)
        for attempt in range(self.max_attempts):
            base_src, _ = self._split_tests(rec["tests"], policy_stale)
            txt = ctx.chat(prompts.REPAIR_SYSTEM,
                           prompts.repair_prompt(fid, sid, rec, decisions, base_src, failing_txt, feedback,
                                                 stale_tests=sorted(stale - policy_stale), kind=kind),
                           "repair", fid, sid, kid, attempt)
            b = extract_blocks(txt)
            code = b.get("MODULE") or (b["_blocks"][0] if b["_blocks"] else None)
            new_tests = b.get("NEW TESTS") or (b["_blocks"][1] if len(b["_blocks"]) > 1 else "")
            if not code or not compiles(code):
                feedback = "The MODULE block was missing or did not compile."
                continue
            if not (new_tests and compiles(new_tests) and "@case" in new_tests) or "import pytest" in new_tests:
                new_tests = ""
            replaced = (self._test_names(new_tests) & (stale - policy_stale)) if new_tests else set()
            old_src, _ = self._split_tests(base_src, replaced)
            combined = old_src.rstrip() + ("\n\n" + new_tests if new_tests else "") + "\n"
            r = run_agent_tests(fid, sid, lib, kid, code=code, tests=combined)
            removed = sorted(policy_stale | replaced)
            if r.get("cases") and not failed_set(r) and not r.get("import_error"):
                self._accept(fid, sid, ms, kid, code, combined, decisions, stamp, f"attempt {attempt + 1}",
                             removed, "stale_or_replaced")
                return
            feedback = summarize_results(r) + "\n(Tests must use sa_testlib only; do not import pytest.)"
            if r.get("cases") and not r.get("import_error"):
                old_names_a = self._test_names(old_src)
                pa = passed_set(r)
                old_pass, new_pass = pa & old_names_a, pa - old_names_a
                # monotone improvement over the version-indexed evidence: nothing that passed may regress
                if (base_pass - {t for t in replaced}) <= old_pass and \
                        (len(old_pass) > len(base_pass) or (kind == "policy" and new_pass)):
                    cand = (len(old_pass), len(new_pass), code, combined, removed)
                    if best is None or cand[:2] > best[:2]:
                        best = cand
            if attempt == self.max_attempts - 1 and r.get("cases") and not r.get("import_error"):
                old_names = self._test_names(old_src)
                bad = [c for c in r["cases"] if not c["passed"]]
                # new, unconfirmed evidence failing while every retained old test passes: keep code, drop them
                if bad and all(c["name"] not in old_names for c in bad):
                    kept, dropped = self._split_tests(combined, {c["name"] for c in bad})
                    self._accept(fid, sid, ms, kid, code, kept, decisions, stamp,
                                 "old evidence passes; unconfirmed new tests dropped", removed + list(dropped),
                                 "unconfirmed_new_tests")
                    return
                # policy change: failing old tests of components judged repair/retire encode the old requirement
                changed = {c for c, d in decisions.items()
                           if str(d.get("decision", "")).lower() in ("repair", "retire")}
                if kind == "policy" and self.use_quarantine and bad and \
                        all(c["component"] in changed for c in bad):
                    kept, dropped = self._split_tests(combined, {c["name"] for c in bad})
                    self._accept(fid, sid, ms, kid, code, kept, decisions, stamp,
                                 "after quarantining evidence of changed components", removed + list(dropped),
                                 "component_changed")
                    return
        if best is not None:
            # partial repair: keep the best attempt; its still-failing evidence stays in the suite so the skill is
            # reviewed again at the next change
            self._accept(fid, sid, ms, kid, best[2], best[3], decisions, stamp,
                         "partial repair (no regressions, net improvement)", best[4], "stale_or_replaced")
            rec["history"][-1]["action"] = "partially_repaired"
            return
        if not broken:
            # the old code still runs in the new runtime: keep it available, record prohibitions as tombstones
            _hist(rec, sid, "repair_not_validated_kept", "old code kept; retired behaviour recorded as tombstones")
            if self.use_tombstones:
                ms["tombstones"].extend(self._tombstones_for(fid, sid, kid, decisions))
            return
        rec["status"] = "quarantined"
        _hist(rec, sid, "quarantined", "repair not validated within budget")
        if self.use_tombstones:
            ms["tombstones"].append({"skill": kid, "component": "*",
                                     "text": f"{kid}: withheld; it could not be validated after the change of "
                                             f"{bench.state(fid, sid)['date']}", "source": "", "date":
                                         bench.state(fid, sid)["date"]})

    def task_context(self, fid, sid, ms):
        c = super().task_context(fid, sid, ms)
        c["tombstones"] = ms["tombstones"] if self.use_tombstones else None
        return c


def _strip_dup_imports(src):
    return src


class LedgerNoQuarantine(SkillLedger):
    name = "ledger_no_quarantine"
    use_quarantine = False


class LedgerNoTombstones(SkillLedger):
    name = "ledger_no_tombstones"
    use_tombstones = False


class LedgerNonSelective(SkillLedger):
    name = "ledger_nonselective"
    selective = False


class SkillLedgerRobust(SkillLedger):
    """Post-hoc amendment A1: the frozen skill_ledger fails open when the impact response is malformed JSON (every
    component is then treated as 'retain'). This variant repairs the structure of the response and, if it still
    cannot be parsed, asks once more. Everything else is identical, and calls are shared with skill_ledger."""
    name = "skill_ledger_robust"
    cache_as = "skill_ledger"

    def _impact(self, fid, sid, sub, ledger, results, ctx):
        prompt = prompts.impact_prompt(fid, sid, sub, ledger, results)
        for attempt in range(2):
            txt = ctx.chat(prompts.IMPACT_SYSTEM, prompt, "impact", fid, sid, attempt=attempt, max_tokens=8000)
            data = extract_json_tolerant(txt)
            if data is not None:
                self.parse_log.append({"state": sid, "attempt": attempt,
                                       "repaired": extract_json(txt) is None})
                return data.get("skills", {})
        self.parse_log.append({"state": sid, "attempt": 2, "failed": True})
        return {}

    def init(self, fid, lib, ctx):
        self.parse_log = []
        return super().init(fid, lib, ctx)


METHODS = {m.name: m for m in (NoSkills, Static, DocRetrieval, VersionAware, Regenerate, RegressionGated,
                               RegressionRefresh, SkillLedger, LedgerNoQuarantine, LedgerNoTombstones,
                               LedgerNonSelective, SkillLedgerRobust)}
POSTHOC_METHODS = {"skill_ledger_robust"}
