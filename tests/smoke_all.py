"""Offline smoke test over every family (dummy model, oracle outputs). No API calls."""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SA_RUNS"] = str(ROOT / "runs_test")
sys.argv = [sys.argv[0]]
import tests.test_pipeline as tp  # noqa: E402,F401  (runs yaml_config + nist_passwords)
from sa import runner, bench  # noqa: E402

fams = bench.families()
runner.run_all(["dummy"], ["static", "regenerate", "skill_ledger", "regression_gated"], [0], fams, max_split="test",
               workers=6)
bad = [l for l in open(ROOT / "runs_test" / "failures.jsonl")] if (ROOT / "runs_test" / "failures.jsonl").exists() else []
print("FAILURES:", len(bad))
for l in bad[:5]:
    print(l[:1500])
