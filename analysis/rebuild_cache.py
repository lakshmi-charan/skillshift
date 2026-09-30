"""Rebuild the model-response cache (runs_main/cache/llm) from the logged calls (runs_main/**/calls.jsonl).

Every uncached model call is logged with its cache key and full response, so the cache is fully determined by the
logs. With the cache in place, `run.py main ...` replays the whole study without any API call.
Usage: python analysis/rebuild_cache.py [runs_dir]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(runs):
    runs = Path(runs)
    n = dup = 0
    for f in sorted(runs.glob("*/*/run*/*/calls.jsonl")):
        for line in open(f, encoding="utf-8"):
            c = json.loads(line)
            key = c.pop("key")
            c.pop("meta", None)
            c.pop("messages", None)
            out = runs / "cache" / "llm" / key[:2] / f"{key}.json"
            if out.exists():
                dup += 1
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
            n += 1
    print(f"wrote {n} cache entries ({dup} already present) under {runs / 'cache' / 'llm'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "runs_main")
