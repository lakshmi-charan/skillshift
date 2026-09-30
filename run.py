"""SkillAdapt experiment driver.

  python run.py check                 # keys, model access (tiny calls), build all environments
  python run.py validate              # benchmark self-validation (reference code passes, epoch-0 code passes s0)
  python run.py labels                # ground-truth retain/repair/retire labels (executable) -> runs/labels.json
  python run.py pilot [--model M]     # development split only, 1 run, all methods -> cost/failure report
  python run.py main  [--model M] [--runs 0,1,2] [--split test]   # full timeline
  python run.py analyze               # tables, figures, evidence index
"""
import argparse
import json
import os
import sys
import time

from sa.common import cfg, load_env, out_dir, write_json, read_json


def cmd_check(a):
    from sa import llm, bench, envs
    env = load_env()
    print("env file:", env or "NOT FOUND (create .env with OPENAI_API_KEY)")
    for k in ("OPENAI_API_KEY", "GROQ_API_KEY"):
        print(f"  {k}: {'set' if os.environ.get(k) else 'missing'}")
    models = a.models.split(",") if a.models else [m["name"] for m in cfg()["models"] if m["provider"] != "dummy"]
    for m in models:
        try:
            r = llm.chat(m, [{"role": "user", "content": "Reply with the single word OK."}], max_tokens=20,
                         stage="check", salt=f"check-{time.time()}")
            print(f"  model {m}: OK ({r['text'].strip()[:20]!r}, {r['latency_s']}s)")
        except Exception as e:
            print(f"  model {m}: FAILED -> {str(e)[:250]}")
    print("building environments ...")
    specs = {}
    for f in bench.families():
        for st in bench.family(f)["states"]:
            specs[envs.spec_key(st["env"])] = st["env"]
    for k, sp in sorted(specs.items()):
        t = time.time()
        try:
            envs.ensure(sp)
            print(f"  {k}: ok ({time.time() - t:.1f}s)")
        except Exception as e:
            print(f"  {k}: FAILED {str(e)[:300]}")
    llm.flush_ledger()


def cmd_validate(a):
    from sa import bench
    ok = True
    for f in (a.families.split(",") if a.families else bench.families()):
        for r in (bench.validate(f), bench.validate_tasks(f)):
            print(f"[{f}] checks={r['checks']} problems={len(r['problems'])}")
            for p in r["problems"]:
                ok = False
                print("   ", json.dumps(p)[:600])
    sys.exit(0 if ok else 1)


def cmd_labels(a):
    from sa import bench
    from sa.runner import split_of
    from collections import Counter
    rows = []
    for f in bench.families():
        for r in bench.labels(f):
            r["split"] = split_of(r["date"])
            rows.append(r)
        print(f, Counter(r["label"] for r in rows if r["family"] == f))
    write_json(out_dir() / "labels.json", rows)
    print("total", Counter((r["split"], r["label"]) for r in rows))


def _families(a):
    return a.families.split(",") if a.families else cfg()["families"]


def cmd_pilot(a):
    from sa import runner, llm
    load_env()
    model = a.model or cfg()["primary_model"]
    methods = a.methods.split(",") if a.methods else cfg()["methods"]
    before = llm.ledger()["total_usd"]
    runner.run_all([model], methods, [0], _families(a), max_split="dev", workers=a.workers or cfg().get("workers", 4))
    print(f"pilot spend: ${llm.ledger()['total_usd'] - before:.3f}")
    from sa import report
    report.pilot_report(model, methods, _families(a))


def cmd_main(a):
    from sa import runner
    load_env()
    model = a.model or cfg()["primary_model"]
    methods = a.methods.split(",") if a.methods else cfg()["methods"] + (cfg()["ablations"] if a.ablations else [])
    runs = [int(x) for x in a.runs.split(",")]
    if a.posthoc:
        _record_posthoc(methods, model, runs)
    else:
        _check_frozen(a.split)
    runner.run_all([model], methods, runs, _families(a), max_split=a.split, workers=a.workers or cfg().get("workers", 4))


def _record_posthoc(methods, model, runs):
    """Post-hoc variants (PROTOCOL.md, Amendments) may run on test events after the freeze, but only methods listed
    in POSTHOC_METHODS, and every such run is logged with the amended tree hash next to the original freeze."""
    from sa.methods import POSTHOC_METHODS
    bad = [m for m in methods if m not in POSTHOC_METHODS]
    if bad:
        sys.exit(f"--posthoc only runs post-hoc variants {sorted(POSTHOC_METHODS)}; refusing {bad}")
    digest, n = _tree_hash()
    path = out_dir() / "posthoc_runs.json"
    log = read_json(path, [])
    log.append({"sha256": digest, "files": n, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "model": model,
                "methods": methods, "runs": runs, "original_freeze": read_json(out_dir() / "protocol_freeze.json")})
    write_json(path, log)
    print("post-hoc run recorded:", digest, n, "files")


def _tree_hash():
    import hashlib
    from pathlib import Path
    root = Path(__file__).resolve().parent
    h, files = hashlib.sha256(), []
    for sub in ("sa", "benchmark"):
        for p in sorted((root / sub).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                files.append(str(p.relative_to(root)))
                h.update(str(p.relative_to(root)).encode()); h.update(p.read_bytes())
    h.update((root / "config.yaml").read_bytes())
    h.update((root / "PROTOCOL.md").read_bytes())
    return h.hexdigest(), len(files)


def cmd_freeze(a):
    digest, n = _tree_hash()
    path = out_dir() / "protocol_freeze.json"
    if path.exists() and not a.force:
        print("already frozen:", read_json(path))
        return
    write_json(path, {"sha256": digest, "files": n, "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                      "protocol": "PROTOCOL.md"})
    print("protocol frozen:", digest, n, "files")


def _check_frozen(split):
    if split != "test":
        return
    fz = read_json(out_dir() / "protocol_freeze.json")
    digest, _ = _tree_hash()
    if not fz or fz["sha256"] != digest:
        sys.exit("Refusing to run test-split events: code/benchmark/config differ from the frozen protocol "
                 "(run `python run.py freeze` first, and do not change files afterwards).")


def cmd_analyze(a):
    from sa import analysis
    analysis.main()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["check", "validate", "labels", "pilot", "freeze", "main", "analyze"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--models")
    ap.add_argument("--methods")
    ap.add_argument("--families")
    ap.add_argument("--runs", default="0")
    ap.add_argument("--split", default="test")
    ap.add_argument("--workers", type=int)
    ap.add_argument("--ablations", action="store_true")
    ap.add_argument("--posthoc", action="store_true")
    a = ap.parse_args()
    load_env()
    {"check": cmd_check, "validate": cmd_validate, "labels": cmd_labels, "pilot": cmd_pilot, "freeze": cmd_freeze, "main": cmd_main,
     "analyze": cmd_analyze}[a.stage](a)


if __name__ == "__main__":
    main()
