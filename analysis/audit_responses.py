"""Audit of recorded model responses (reads runs_main/**/calls.jsonl; no API calls).

Counts, per model and method: impact responses that the frozen parser (extract_json) cannot read, how many the
post-hoc tolerant parser recovers, and responses cut off by the output-token limit. Writes <runs>/response_audit.json.
Usage: python analysis/audit_responses.py [runs_dir]"""
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sa.library import extract_json, extract_json_tolerant  # noqa: E402

runs = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "runs_main"
out = defaultdict(lambda: {"impact_calls": 0, "impact_unparsed": 0, "impact_recovered": 0, "truncated": 0,
                           "calls": 0, "unparsed_where": []})
for f in sorted(glob.glob(str(runs / "*" / "*" / "run*" / "*" / "calls.jsonl"))):
    model, method, run, fam = Path(f).parts[-5:-1]
    for line in open(f, encoding="utf-8"):
        c = json.loads(line)
        d = out[f"{model}/{method}"]
        d["calls"] += 1
        d["truncated"] += c.get("finish_reason") == "length"
        if c.get("stage") == "impact":
            d["impact_calls"] += 1
            if extract_json(c["text"]) is None:
                d["impact_unparsed"] += 1
                d["impact_recovered"] += extract_json_tolerant(c["text"]) is not None
                d["unparsed_where"].append(f"{run}/{fam}/{c['meta']['state']}")
(runs / "response_audit.json").write_text(json.dumps(out, indent=1))
for k, v in sorted(out.items()):
    print(k, {x: y for x, y in v.items() if x != "unparsed_where"})
