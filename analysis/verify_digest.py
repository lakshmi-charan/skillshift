"""Check the published code against the protocol digests recorded during the study.

runs_main/protocol_freeze.json holds the digest taken before the first test-split event, and
runs_main/posthoc_runs.json the digest of the code used for the post-hoc Amendment A1. The per-file manifests in
analysis/ (frozen_manifest.json, asrun_manifest.json) list the sha256 of every file those digests cover, so each
published file can be compared with the version that was actually run.

Usage: python analysis/verify_digest.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Files edited after the study for publication only (default paths of document-fetching tools; not used by any
# experiment). Every other difference is reported as unexpected.
PUBLICATION_EDITS = {"benchmark/tools/make_nist_docs.py", "benchmark/tools/make_legacy_crypto_docs.py",
                     "benchmark/tools/make_tls_docs.py", "benchmark/AUTHORING.md"}


def current_files():
    files = []
    for sub in ("sa", "benchmark"):
        for p in sorted((ROOT / sub).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                files.append(p)
    files += [ROOT / "config.yaml", ROOT / "PROTOCOL.md"]
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def compare(name, manifest_path, expected_extra=()):
    man = json.loads(manifest_path.read_text())["files"]
    man = {k.replace("\\", "/"): v for k, v in man.items()}
    cur = current_files()
    changed = sorted(k for k in man if k in cur and cur[k] != man[k])
    missing = sorted(k for k in man if k not in cur)
    added = sorted(k for k in cur if k not in man)
    expected = PUBLICATION_EDITS | set(expected_extra)
    unexpected = [k for k in changed + missing + added if k not in expected]
    print(f"\n{name}: {len(man)} files in manifest, {len(cur)} files now")
    for label, lst in (("changed", changed), ("missing", missing), ("added", added)):
        for k in lst:
            tag = "expected" if k in expected else "UNEXPECTED"
            print(f"  {label:8s} {k}  ({tag})")
    print("  result:", "OK" if not unexpected else f"{len(unexpected)} unexpected difference(s)")
    return not unexpected


def main():
    import run
    digest, n = run._tree_hash()
    print(f"digest of the published tree: {digest} ({n} files)")
    fz = json.loads((ROOT / "runs_main" / "protocol_freeze.json").read_text())
    ph = json.loads((ROOT / "runs_main" / "posthoc_runs.json").read_text())
    print(f"recorded freeze digest:       {fz['sha256']} ({fz['files']} files)")
    print(f"recorded amendment digest:    {ph[0]['sha256']} ({ph[0]['files']} files)")
    ok_a = compare("Amendment A1 (code used for the post-hoc runs)", ROOT / "analysis" / "asrun_manifest.json")
    # between the freeze and A1: the post-hoc variant (sa/library.py, sa/methods.py, sa/runner.py), the amendment
    # text (PROTOCOL.md) and the figure module added for the analysis (sa/figures.py); frozen copies of the first
    # four are in analysis/frozen_code/.
    ok_f = compare("Freeze before the test split", ROOT / "analysis" / "frozen_manifest.json",
                   expected_extra={"sa/library.py", "sa/methods.py", "sa/runner.py", "PROTOCOL.md", "sa/figures.py"})
    man = {k.replace("\\", "/"): v for k, v in
           json.loads((ROOT / "analysis" / "frozen_manifest.json").read_text())["files"].items()}
    ok_c = True
    print("\nFrozen copies in analysis/frozen_code/:")
    for rel in ("sa/library.py", "sa/methods.py", "sa/runner.py", "PROTOCOL.md"):
        h = hashlib.sha256((ROOT / "analysis" / "frozen_code" / rel).read_bytes()).hexdigest()
        good = h == man.get(rel)
        ok_c &= good
        print(f"  {rel:16s} {'matches the freeze manifest' if good else 'DOES NOT MATCH'}")
    sys.exit(0 if ok_a and ok_f and ok_c else 1)


if __name__ == "__main__":
    main()
