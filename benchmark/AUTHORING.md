# Authoring a benchmark family

A **family** is a small library of reusable skills (Python modules) plus the dated sequence of real
changes (library releases and/or policy revisions) that affect them. Everything is executable.
Read `families/yaml_config` (tool change) and `families/password_storage` (policy change) first; they are
the reference examples. Run the validator often.

## Non-negotiable rules

1. **Real, dated, documented events only.** Every state transition corresponds to a real release or a real
   policy revision with its official date. Never invent a change.
2. **Verbatim documentation, fetched by script.** The text an agent receives for an event (`docs/*.md`)
   must be copied programmatically from the primary source (e.g. `curl` of a raw GitHub changelog, then
   `sed` to cut the section). Never type or paraphrase release notes from memory. Put the source URL and
   fetch date at the top of each doc. If you cannot fetch a source, stop and report it; do not substitute.
   Put the fetch commands in `benchmark/tools/make_<family>_docs.py` (or `.sh`) so the docs are reproducible.
   Keep a doc to the relevant section(s) of the release notes (about 1-12 KB); irrelevant items within that
   section may stay (realistic noise).
3. **Every behaviour is verified by execution in the real library version.** Use `python -m sa.cli_bench
   validate <family>` and `labels <family>`; both must be clean before you finish.
4. **Epoch-0 skills are realistic code of their era.** Write each skill as a competent developer would have
   written it against the s0 versions, using idioms that were documented/common then (e.g. `df.append`
   with pandas 1.5, `engine.execute` with SQLAlchemy 1.4). Each epoch-0 skill must pass all its s0 hidden and
   visible tests. Do not write code that is "future-proof" on purpose; do not write deliberately broken code.
5. **Include still-valid skills/components.** Roughly 40-60% of components should be unaffected by any given
   event (label `retain`). Retention of still-valid behaviour is a primary measurement.

## Directory layout

```
families/<id>/
  family.yaml            # spec (below)
  skills/<skill>.py      # epoch-0 library code (what the agent starts with)
  visible/test_<skill>.py  # the library's own historical tests, written in the s0 era (agents can run these)
  hidden/test_<skill>.py   # evaluation tests (agents never see these); may import a local helper module
  refs/<state>/<skill>.py  # reference (correct) code for that state; omit if unchanged from the previous state.
                           # A file containing exactly '# RETIRED' means the whole skill must be absent.
  docs/*.md              # verbatim event documentation (+ policy text in force at s0 for policy families)
  tasks/<task>.yaml      # downstream tasks (below)
  tasks/test_<task>.py   # hidden tests for a task
  tasks/refs/<task>.py   # reference solution valid at s0; tasks/refs/<state>/<task>.py overrides from that state on
```

## family.yaml

```yaml
id: <family id>
title: ...
domain: tool | policy | interaction
summary: >  one paragraph shown to agents (the deployment context; no hints about future changes)
standing_policy: [ {id, text, source} ]   # optional rules that hold in every state
states:
  - id: s0
    date: "YYYY-MM-DD"            # release date of the s0 versions (or policy revision date)
    label: "pandas 1.5.3"
    env: {python: "3.11", packages: {pandas: "1.5.3", numpy: "1.26.4"}}   # exact pins; wheels must exist
    policy_doc: docs/...          # policy families only: policy text in force
  - id: s1
    date: "2023-04-03"            # official date of the event
    label: "pandas 2.0.3"
    env: {...}                    # usually: last patch release of the breaking version line
    event: {id: pandas-2.0, kind: tool|policy, title: "...", source: "<primary URL>", doc: docs/pandas-2.0.md}
skills:
  - id: <skill id>                # also the module name
    file: skills/<id>.py
    visible_tests: visible/test_<id>.py
    hidden_tests: hidden/test_<id>.py
    purpose: "one line"
    components:                   # 2-6 independently testable behaviours
      - {id: <component>, requirement: "one sentence, version-neutral"}
```

Rules for states: hold everything fixed except what the event changes (e.g. keep the Python version constant
across library states if the library supports it). If an event id is shared with another family (e.g.
`python-3.12`), use the same id and date.

## Tests

Test files use the tiny library `sa_testlib` injected by the runner (no pytest):

```python
from sa_testlib import case, need, getfn, STATE

@case("component_id")                       # kind="valid" (default), states="*" (default)
def h_something(mod):                        # mod = the skill module under test (None if absent)
    f = need(mod, "function_name")            # raises (test fails) if the function is absent
    assert f(...) == ...

@case("component_id", kind="policy")        # a constraint that must hold (policy violation if it fails)
@case("component_id", kind="obsolete", states=["s2"])   # passes iff the prohibited behaviour is ABSENT:
def o_gone(mod):                             # use getfn(mod, name) -> None if absent; absent or refusing counts as retired
    f = getfn(mod, "old_function")
    if f is None: return
    ...assert the prohibited behaviour does not happen (e.g. it raises PermissionError/ValueError)...
```

* `states=[...]` restricts a case to states where the requirement exists. `STATE` is the current state id.
* Hidden tests check the **requirement** of each component in each state; they must be thorough (edge cases,
  2-4 cases per component) and must not depend on implementation details not in the requirement.
* Tests run with a per-test timeout (20 s); keep each under ~2 s. No network access. Use `tempfile` for files.
* Skills of the same family are importable by module name from each other and from task solutions.
* Visible tests encode what the library's authors tested in the s0 era, including version-specific
  expectations that later become stale (e.g. exact parameter values). 2-4 tests per skill.

## Downstream tasks (3-5 per family)

```yaml
id: <task id>
function: <main function name>
relevant_skills: [<skill ids>]      # for analysis only; never shown to agents
prompt: |
  Write a Python function `name(args) -> type` that ...   # a concrete request a developer would make;
  # it must be solvable in every state; do not mention versions or policies explicitly.
tests: tasks/test_<task id>.py
```

Task tests use the same `case` decorator; components are free-form names (`functional`, or a policy name with
kind="policy"; a request that becomes prohibited in a later state must expect `PermissionError` in those states
via states=[...]). Provide reference solutions in `tasks/refs/` that pass in every state.

## Validation (must be clean)

```
cd skillshift   # repository root
SA_UV=/usr/local/bin/uv python3 -m sa.cli_bench validate <family>   # epoch-0 passes s0; refs pass their states; tasks refs pass
SA_UV=/usr/local/bin/uv python3 -m sa.cli_bench labels <family>     # shows retain/repair/retire per component per event
```

Check the labels make sense: every event should produce at least one `repair` or `retire`; each skill should have
components that are `retain` for some event.
