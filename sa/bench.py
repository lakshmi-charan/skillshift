"""Benchmark loading, ground-truth labelling and self-validation."""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import yaml

from .common import BENCH, write_json, read_json, out_dir
from . import execute


def fam_dir(fid):
    return BENCH / "families" / fid


@lru_cache(maxsize=None)
def family(fid):
    d = fam_dir(fid)
    spec = yaml.safe_load((d / "family.yaml").read_text(encoding="utf-8"))
    spec["dir"] = str(d)
    for i, st in enumerate(spec["states"]):
        st["index"] = i
    return spec


def families():
    return sorted(p.name for p in (BENCH / "families").iterdir() if (p / "family.yaml").exists())


def state(fid, sid):
    return next(s for s in family(fid)["states"] if s["id"] == sid)


def skill(fid, kid):
    return next(k for k in family(fid)["skills"] if k["id"] == kid)


def read(fid, rel):
    return (fam_dir(fid) / rel).read_text(encoding="utf-8")


def ref_code(fid, kid, sid):
    """Correct library code for skill kid in state sid (falls back to the latest earlier state).
    A reference file containing only '# RETIRED' means the whole skill should be absent."""
    fam = family(fid)
    idx = state(fid, sid)["index"]
    for st in reversed(fam["states"][: idx + 1]):
        p = fam_dir(fid) / "refs" / st["id"] / f"{kid}.py"
        if p.exists():
            txt = p.read_text(encoding="utf-8")
            return None if txt.strip() == "# RETIRED" else txt
    return read(fid, skill(fid, kid)["file"])


def siblings(fid, kid, library):
    """Other skills of the family as importable modules (absent/retired skills are omitted)."""
    return {f"{k}.py": c for k, c in (library or {}).items() if k != kid and c is not None}


def ref_library(fid, sid):
    return {sk["id"]: ref_code(fid, sk["id"], sid) for sk in family(fid)["skills"]}


def run_hidden(fid, kid, sid, code, library=None):
    sk = skill(fid, kid)
    lib = ref_library(fid, sid) if library is None else library
    return execute.run_tests(state(fid, sid)["env"], code, fam_dir(fid) / sk["hidden_tests"], sid,
                             module_name=kid, extra_files=siblings(fid, kid, lib))


def run_visible(fid, kid, sid, code, tests_path=None, library=None):
    sk = skill(fid, kid)
    tp = tests_path or (fam_dir(fid) / sk["visible_tests"])
    lib = ref_library(fid, sid) if library is None else library
    return execute.run_tests(state(fid, sid)["env"], code, tp, sid, module_name=kid,
                             extra_files=siblings(fid, kid, lib))


def component_outcomes(res):
    """Map component -> dict(kind, passed_all, n, n_pass)."""
    out = {}
    for c in res.get("cases", []):
        o = out.setdefault(c["component"], {"kind": c["kind"], "n": 0, "n_pass": 0})
        o["n"] += 1
        o["n_pass"] += int(bool(c["passed"]))
    for o in out.values():
        o["passed_all"] = o["n_pass"] == o["n"]
    return out


def labels(fid, n_jobs=1):
    """Ground-truth retain/repair/retire labels for every event, from executing reference code."""
    fam = family(fid)
    rows = []
    for st in fam["states"][1:]:
        prev = fam["states"][st["index"] - 1]
        for sk in fam["skills"]:
            before = ref_code(fid, sk["id"], prev["id"])
            # neighbours at their correct new-state versions, so the label reflects this skill's own code
            res = run_hidden(fid, sk["id"], st["id"], before, library=ref_library(fid, st["id"]))
            outc = component_outcomes(res)
            for comp, o in outc.items():
                if o["kind"] == "obsolete":
                    lab = "retire" if not o["passed_all"] else "absent"
                else:
                    lab = "retain" if o["passed_all"] else "repair"
                rows.append({"family": fid, "event": st["event"]["id"], "state": st["id"], "date": st["date"],
                             "kind_event": st["event"]["kind"], "skill": sk["id"], "component": comp,
                             "component_kind": o["kind"], "label": lab})
    return rows


def validate(fid):
    """Check (1) epoch-0 code passes all s0 hidden+visible tests, (2) each state's reference passes its
    hidden tests, (3) visible tests pass for s0 code. Returns report dict."""
    fam = family(fid)
    rep = {"family": fid, "problems": [], "checks": 0}
    s0 = fam["states"][0]["id"]
    for sk in fam["skills"]:
        code0 = read(fid, sk["file"])
        lib0 = {k["id"]: read(fid, k["file"]) for k in fam["skills"]}
        for kind, res in (("hidden", run_hidden(fid, sk["id"], s0, code0, library=lib0)),
                          ("visible", run_visible(fid, sk["id"], s0, code0, library=lib0))):
            rep["checks"] += 1
            bad = [c for c in res.get("cases", []) if not c["passed"]]
            if res.get("fatal") or res.get("import_error") or bad or not res.get("cases"):
                rep["problems"].append({"skill": sk["id"], "state": s0, "which": f"epoch0-{kind}",
                                        "fatal": res.get("fatal"), "import_error": res.get("import_error"),
                                        "failed": [(c["name"], c["error"]) for c in bad]})
        for st in fam["states"][1:]:
            code = ref_code(fid, sk["id"], st["id"])
            res = run_hidden(fid, sk["id"], st["id"], code)
            rep["checks"] += 1
            bad = [c for c in res.get("cases", []) if not c["passed"]]
            if res.get("fatal") or bad:
                rep["problems"].append({"skill": sk["id"], "state": st["id"], "which": "reference-hidden",
                                        "fatal": res.get("fatal"), "import_error": res.get("import_error"),
                                        "failed": [(c["name"], c["error"]) for c in bad]})
    return rep


# ------------------------------------------------------------------ downstream tasks ----
@lru_cache(maxsize=None)
def tasks(fid):
    d = fam_dir(fid) / "tasks"
    out = []
    for p in sorted(d.glob("*.yaml")):
        t = yaml.safe_load(p.read_text(encoding="utf-8"))
        t["family"] = fid
        out.append(t)
    return out


def task(fid, tid):
    return next(t for t in tasks(fid) if t["id"] == tid)


def task_ref(fid, tid, sid):
    fam = family(fid)
    idx = state(fid, sid)["index"]
    for st in reversed(fam["states"][: idx + 1]):
        p = fam_dir(fid) / "tasks" / "refs" / st["id"] / f"{tid}.py"
        if p.exists():
            return p.read_text(encoding="utf-8")
    return (fam_dir(fid) / "tasks" / "refs" / f"{tid}.py").read_text(encoding="utf-8")


def run_task(fid, tid, sid, code, library=None):
    """Run a downstream task's hidden tests on generated code. `library` (skill_id -> code) is importable."""
    t = task(fid, tid)
    extra = {f"{k}.py": c for k, c in (library or {}).items() if c is not None}
    return execute.run_tests(state(fid, sid)["env"], code, fam_dir(fid) / t["tests"], sid,
                             module_name="solution", extra_files=extra)


def validate_tasks(fid):
    rep = {"family": fid, "problems": [], "checks": 0}
    for t in tasks(fid):
        for st in family(fid)["states"]:
            res = run_task(fid, t["id"], st["id"], task_ref(fid, t["id"], st["id"]))
            rep["checks"] += 1
            bad = [c for c in res.get("cases", []) if not c["passed"]]
            if res.get("fatal") or res.get("import_error") or bad or not res.get("cases"):
                rep["problems"].append({"task": t["id"], "state": st["id"], "fatal": res.get("fatal"),
                                        "import_error": res.get("import_error"),
                                        "failed": [(c["name"], c["error"]) for c in bad]})
    return rep
