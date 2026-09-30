"""Prompt builders. All methods receive the same deployment context and the same change documentation;
they differ only in what they store and how they update it."""
import json

from . import bench, envs
from .library import signatures, api_dependencies

MAX_DOC_CHARS = 16000
MAX_BUNDLE_CHARS = 44000

TESTLIB = """Tests use the small runner library `sa_testlib` (not pytest):
```python
from sa_testlib import case, need, getfn
@case("<component_id>")                      # a behaviour that must hold
def t_name(mod):                             # mod = the skill module (None if absent)
    f = need(mod, "function_name")           # fails the test if the function is missing
    assert f(...) == ...
@case("<component_id>", kind="obsolete")    # passes iff a prohibited behaviour is ABSENT
def t_gone(mod):
    f = getfn(mod, "function_name")          # None if absent
    if f is None: return
    try: f(...)
    except PermissionError: return
    raise AssertionError("prohibited behaviour still performed")
```
Other library modules of the same family are importable by module name. Do not import pytest. Keep each test under
~2 seconds."""


# ----------------------------------------------------------------------------- context
def env_text(fid, sid):
    spec = bench.state(fid, sid)["env"]
    try:
        info = envs.info(spec)
        pk = info.get("packages", {})
        wanted = [p.lower() for p in (spec.get("packages") or {})]
        shown = ", ".join(f"{p}=={pk.get(p, pk.get(p.replace('_', '-'), '?'))}" for p in wanted)
        py = info.get("python", spec["python"])
    except Exception:
        shown = ", ".join(f"{k}=={v}" for k, v in (spec.get("packages") or {}).items())
        py = spec["python"]
    return f"Python {py}" + (f"; installed packages: {shown}" if shown else "; standard library only")


def family_text(fid):
    fam = bench.family(fid)
    s = f"Domain: {fam['title']}\n{fam.get('summary', '').strip()}"
    for sp in fam.get("standing_policy") or []:
        s += f"\nStanding rule ({sp['id']}): {sp['text']}"
    return s


def clip(text, n=MAX_DOC_CHARS):
    if len(text) <= n:
        return text
    return text[: n - 200] + f"\n\n[... document truncated: {len(text) - n + 200} more characters ...]"


def policy_text(fid, sid):
    st = bench.state(fid, sid)
    if not st.get("policy_doc"):
        return ""
    return clip(bench.read(fid, st["policy_doc"]))


def event_doc(fid, sid):
    st = bench.state(fid, sid)
    ev = st.get("event")
    if not ev:
        return ""
    return (f"Change: {ev['title']}\nDate: {st['date']}\nSource: {ev.get('source', '')}\n\n"
            + clip(bench.read(fid, ev["doc"])))


def docs_bundle(fid, sid):
    """Current documentation available to documentation-retrieval agents: the policy text in force (policy
    families) plus the change documents of all events so far, newest first."""
    fam = bench.family(fid)
    idx = bench.state(fid, sid)["index"]
    parts = []
    pt = policy_text(fid, sid)
    if pt:
        parts.append("=== Policy text currently in force ===\n" + pt)
    for st in reversed(fam["states"][1: idx + 1]):
        parts.append("=== " + st["event"]["title"] + " ===\n" + event_doc(fid, st["id"]))
    out, n = [], 0
    for p in parts:
        if n + len(p) > MAX_BUNDLE_CHARS:
            out.append(clip(p, max(2000, MAX_BUNDLE_CHARS - n)))
            break
        out.append(p)
        n += len(p)
    return "\n\n".join(out)


def contract_text(rec):
    lines = [f"Purpose: {rec['purpose']}", "Components (behaviours of this skill):"]
    for c in rec["components"]:
        lines.append(f"  - {c['id']}: {c['requirement']}")
    return "\n".join(lines)


def skill_block(rec, with_tests=False):
    s = f"### Module `{rec['id']}`\n{contract_text(rec)}\n```python\n{rec['code']}\n```"
    if with_tests:
        s += f"\nIts tests:\n```python\n{rec['tests']}\n```"
    return s


# ----------------------------------------------------------------------------- downstream tasks
TASK_SYSTEM = ("You are a software engineer working inside an organisation's codebase. Write correct, complete "
               "Python code for the request. Follow the organisation's rules that are currently in force. If "
               "carrying out a request would violate a rule currently in force, the requested function must raise "
               "PermissionError with a short explanation instead of performing the prohibited operation. Reply with "
               "one ```python block containing the complete module and nothing else.")


def task_prompt(fid, sid, task, skills=None, tombstones=None, docs=None):
    parts = [f"## Deployment context\n{family_text(fid)}", f"## Runtime\n{env_text(fid, sid)}"]
    if skills:
        parts.append("## Skill library (importable modules you may reuse; import them by module name)\n"
                     + "\n\n".join(skill_block(r) for r in skills))
    if tombstones:
        parts.append("## Retired procedures (do not reintroduce these behaviours)\n"
                     + "\n".join(f"- {t['text']} (source: {t.get('source', '')}; since {t.get('date', '')})"
                                 for t in tombstones))
    if docs:
        parts.append("## Documentation\n" + docs)
    parts.append(f"## Request\n{task['prompt'].strip()}")
    return "\n\n".join(parts)


# ----------------------------------------------------------------------------- adaptation (shared pieces)
def change_context(fid, sid):
    parts = [f"## Deployment context\n{family_text(fid)}", f"## New runtime\n{env_text(fid, sid)}",
             f"## Change that just took effect\n{event_doc(fid, sid)}"]
    pt = policy_text(fid, sid)
    if pt:
        parts.append(f"## Policy text now in force\n{pt}")
    return "\n\n".join(parts)


# ----------------------------------------------------------------------------- SkillLedger
LEDGER_SYSTEM = ("You maintain a library of reusable code skills for an engineering organisation. You record why each "
                 "behaviour exists so that it can be re-checked when tools or rules change. Answer with JSON only.")


def ledger_setup_prompt(fid, sid, lib):
    skills = []
    for rec in lib.values():
        skills.append(f"{skill_block(rec, with_tests=True)}\nDetected API dependencies: "
                      f"{', '.join(api_dependencies(rec['code'])[:60])}")
    pt = policy_text(fid, sid)
    return (f"## Deployment context\n{family_text(fid)}\n\n## Runtime\n{env_text(fid, sid)}\n\n"
            + (f"## Policy text in force\n{pt}\n\n" if pt else "")
            + "## Skills\n" + "\n\n".join(skills) + "\n\n"
            "## Task\nFor every component of every skill, record its grounds: (a) the library/runtime APIs it relies "
            "on (dotted names) and (b) the exact sentence(s) of the policy text or deployment context that require or "
            "permit the behaviour, quoted verbatim (empty list if none). For every test function, record which "
            "component it evidences and which grounds its expected values come from.\n"
            "Return JSON: {\"skills\": {\"<skill>\": {\"components\": {\"<component>\": {\"apis\": [..], "
            "\"quotes\": [..]}}, \"tests\": {\"<test function>\": {\"component\": \"..\", \"depends_on\": "
            "\"api|policy|both|none\", \"quote\": \"..\"}}}}}")


IMPACT_SYSTEM = ("You maintain a library of reusable code skills. A tool or rule change has just taken effect. Decide, "
                 "component by component, whether each recorded behaviour is still valid (retain), must be changed to "
                 "stay correct and permitted (repair), or is no longer permitted at all (retire). Retire only behaviour "
                 "that the new rules prohibit or that has lost its purpose; keep everything that is still valid. Answer "
                 "with JSON only.")


def impact_prompt(fid, sid, lib, ledger, test_results):
    blocks = []
    for kid, rec in lib.items():
        if rec["status"] == "retired":
            continue
        led = ledger.get(kid, {})
        res = test_results.get(kid, {})
        failing = [c for c in res.get("cases", []) if not c["passed"]]
        fail_txt = "\n".join(f"    FAIL {c['name']}: {c['error'][:300]}" for c in failing[:10]) or "    (none)"
        if res.get("import_error"):
            fail_txt = f"    IMPORT ERROR: {res['import_error']}\n" + fail_txt
        grounds = json.dumps(led.get("components", {}), ensure_ascii=False)[:3000]
        tests = json.dumps(led.get("tests", {}), ensure_ascii=False)[:3000]
        blocks.append(f"{skill_block(rec)}\nRecorded grounds (validated under: {led.get('validated_under', '?')}): "
                      f"{grounds}\nRecorded test evidence: {tests}\nVisible test results in the NEW runtime:\n{fail_txt}")
    return (change_context(fid, sid) + "\n\n## Library\n" + "\n\n".join(blocks) + "\n\n## Task\n"
            "For each skill and component decide: \"retain\" (still valid and permitted as is), \"repair\" (still "
            "required/permitted but the code or parameters must change), or \"retire\" (a rule now prohibits the "
            "behaviour; it must be removed or refuse with PermissionError). A library or runtime change alone never "
            "justifies \"retire\": if an API was removed, the behaviour is repaired with a replacement. For each test "
            "function decide whether its EXPECTED RESULT is still correct under the new tools and rules (\"valid\") "
            "or encodes a requirement or documented result that no longer holds (\"stale\"). A test that fails only "
            "because the code uses a removed API is still \"valid\". For every retired component write one sentence "
            "stating the prohibition and cite the governing text.\n"
            "Return JSON: {\"skills\": {\"<skill>\": {\"components\": {\"<component>\": {\"decision\": "
            "\"retain|repair|retire\", \"reason\": \"..\", \"prohibition\": \"(retire only)\", \"source\": "
            "\"(quote)\"}}, \"tests\": {\"<test function>\": \"valid|stale\"}}}}")


REPAIR_SYSTEM = ("You maintain a library of reusable code skills. Update one skill module after a tool or rule change, "
                 "making the smallest change that keeps every still-valid behaviour intact.")


def repair_prompt(fid, sid, rec, decisions, valid_tests_src, failing_txt, feedback=None, stale_tests=(), kind="tool"):
    dec_lines = []
    for c in rec["components"]:
        d = decisions.get(c["id"], {"decision": "retain"})
        extra = f" — {d.get('reason', '')}" if d.get("decision") != "retain" else ""
        dec_lines.append(f"  - {c['id']} [{d.get('decision', 'retain').upper()}]{extra}")
    fb = f"\n\n## Your previous attempt failed\n{feedback}" if feedback else ""
    return (change_context(fid, sid) + f"\n\n## Skill to update\n{skill_block(rec)}\n\n"
            f"## Decisions per component\n" + "\n".join(dec_lines) + "\n"
            "RETAIN: keep the behaviour exactly. REPAIR: change the code so the behaviour is correct under the new "
            "tools and rules. RETIRE: remove the behaviour, or make the function raise PermissionError when asked to "
            "perform it; do not remove other behaviour of the same function.\n\n"
            f"## Tests that remain valid (they must keep passing)\n```python\n{valid_tests_src}\n```\n"
            f"Current failures in the new runtime:\n{failing_txt}{fb}\n\n"
            + (f"Tests judged possibly stale: {', '.join(stale_tests)}. Only if the change document shows that their "
               "expected result really changed, include corrected versions WITH THE SAME FUNCTION NAMES in NEW TESTS; "
               "otherwise they must keep passing.\n\n" if stale_tests else "") +
            f"## Output\n{TESTLIB}\n\nReply with exactly two blocks:\n### MODULE\n```python\n<the complete updated "
            "module>\n```\n### NEW TESTS\n```python\n<new test functions (with imports) that check each REPAIRED and "
            "RETIRED component against the new tools/rules; component ids as above>\n```")


# ----------------------------------------------------------------------------- regeneration baseline
REGEN_SYSTEM = ("You write reusable code skills for an engineering organisation. Implement a skill from its "
                "specification so that it is correct for the current tools and rules.")


def regen_prompt(fid, sid, rec, feedback=None):
    stub = signatures(rec["code"])
    fb = f"\n\n## Your previous attempt failed its own tests\n{feedback}" if feedback else ""
    return (f"## Deployment context\n{family_text(fid)}\n\n## Runtime\n{env_text(fid, sid)}\n\n"
            f"## Current documentation\n{docs_bundle(fid, sid)}\n\n"
            f"## Skill specification: module `{rec['id']}`\n{contract_text(rec)}\nPublic interface to provide:\n"
            f"```python\n{stub}\n```{fb}\n\n"
            "Write the module from scratch for the current runtime and the rules currently in force. If the current "
            "rules prohibit a component, the corresponding call must raise PermissionError (or omit it); if they "
            "prohibit the whole skill, reply with the single line RETIRED instead of code.\n\n"
            f"{TESTLIB}\n\nReply with exactly two blocks:\n### MODULE\n```python\n<module>\n```\n### NEW TESTS\n"
            "```python\n<tests for every component, using sa_testlib>\n```")


# ----------------------------------------------------------------------------- regression-gated baseline
PROPOSE_SYSTEM = ("You improve a library of reusable code skills. Propose an edit to one skill so that it works "
                  "correctly under the current tools and rules.")


def propose_prompt(fid, sid, rec, failing_txt, variant):
    return (change_context(fid, sid) + f"\n\n## Skill\n{skill_block(rec, with_tests=True)}\n\n"
            f"## Test results in the new runtime\n{failing_txt}\n\n"
            f"Propose candidate edit #{variant}: an updated version of the module (you may add, change, or remove "
            "behaviour, or make a prohibited operation raise PermissionError). Reply with one block:\n### MODULE\n"
            "```python\n<complete module>\n```")


REFRESH_SYSTEM = ("You maintain the regression test suite of a code skill library. Update tests so that they check "
                  "the behaviour required by the current tools and rules.")


def refresh_prompt(fid, sid, rec):
    return (change_context(fid, sid) + f"\n\n## Skill and its current tests\n{skill_block(rec, with_tests=True)}\n\n"
            "Rewrite the test module so that every expectation reflects the current tools and rules: keep tests that "
            "are still correct, fix expectations that changed, and turn expectations for prohibited behaviour into "
            f"tests that the behaviour is refused or absent (kind=\"obsolete\").\n\n{TESTLIB}\n\nReply with one "
            "block:\n### TESTS\n```python\n<complete test module>\n```")
