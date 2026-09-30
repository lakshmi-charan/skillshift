"""python -m sa.cli_bench validate|labels [family ...]"""
import json
import sys
from collections import Counter

from . import bench


def main():
    cmd = sys.argv[1]
    fams = sys.argv[2:] or bench.families()
    if cmd == "validate":
        ok = True
        for f in fams:
            for r in (bench.validate(f), bench.validate_tasks(f)):
                print(f"[{f}] checks={r['checks']} problems={len(r['problems'])}")
                for p in r["problems"]:
                    ok = False
                    print("   ", json.dumps(p)[:700])
        sys.exit(0 if ok else 1)
    if cmd == "labels":
        for f in fams:
            rows = bench.labels(f)
            for r in rows:
                print(f"  {r['event']:<22} {r['skill']:<18} {r['component']:<24} {r['component_kind']:<8} {r['label']}")
            print(f"[{f}]", Counter(r["label"] for r in rows))


if __name__ == "__main__":
    main()
