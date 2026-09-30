"""Offline end-to-end check of the whole pipeline with a scripted 'dummy' model (no API calls).
The dummy returns reference code, so adaptive methods should end with passing libraries."""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SA_RUNS"] = str(ROOT / "runs_test")
shutil.rmtree(ROOT / "runs_test", ignore_errors=True)

from sa import llm, bench, runner  # noqa: E402


def dummy(model, msgs, meta):
    st, fid, sid, kid = meta.get("stage"), meta.get("family"), meta.get("state"), meta.get("skill")
    if st == "task":
        return "```python\n" + bench.task_ref(fid, kid, sid) + "\n```"
    if st in ("repair", "regenerate", "propose"):
        code = bench.ref_code(fid, kid, sid)
        if code is None:
            return "RETIRED" if st == "regenerate" else "### MODULE\n```python\ndef _retired():\n    pass\n```"
        return "### MODULE\n```python\n" + code + "\n```\n### NEW TESTS\n```python\nfrom sa_testlib import case\n```"
    if st == "impact":
        labels = [r for r in bench.labels(fid) if r["state"] == sid]
        out = {"skills": {}}
        for r in labels:
            d = {"retain": "retain", "repair": "repair", "retire": "retire", "absent": "retain"}[r["label"]]
            out["skills"].setdefault(r["skill"], {"components": {}, "tests": {}})["components"][r["component"]] = \
                {"decision": d, "reason": "dummy", "prohibition": "dummy prohibition"}
        return "```json\n" + json.dumps(out) + "\n```"
    if st == "ledger_setup":
        return "```json\n{\"skills\": {}}\n```"
    return "```python\n```"


llm.set_dummy(dummy)
fams = sys.argv[1:] or ["yaml_config", "nist_passwords"]
methods = ["no_skills", "static", "doc_retrieval", "version_aware", "regenerate", "regression_gated",
           "regression_refresh", "skill_ledger"]
runner.run_all(["dummy"], methods, [0], fams, max_split="test", workers=4)
for m in methods:
    for f in fams:
        recs = json.load(open(ROOT / "runs_test" / "dummy" / m / "run0" / f / "records.json"))
        last = recs[-1]
        post = last["post"] or {}
        n = sum(len(v["cases"]) for v in post.values())
        p = sum(c["passed"] for v in post.values() for c in v["cases"])
        t = sum(all(c["passed"] for c in x["cases"]) and bool(x["cases"]) for x in last["tasks"])
        print(f"{m:<20} {f:<16} library {p}/{n}  tasks {t}/{len(last['tasks'])}  status={last.get('status')}")
