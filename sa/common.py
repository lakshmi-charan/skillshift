"""Shared helpers: paths, config, .env loading, JSON I/O, hashing."""
import hashlib
import json
import os
import threading
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "benchmark"
_LOCK = threading.Lock()
_CFG = None


def load_env(path=None):
    """Minimal .env loader (KEY=VALUE per line). Never prints values."""
    cands = [Path(path)] if path else [ROOT / ".env", Path.cwd() / ".env"]
    for p in cands:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v and k not in os.environ:
                    os.environ[k] = v
            return str(p)
    return None


def cfg():
    global _CFG
    if _CFG is None:
        p = os.environ.get("SA_CONFIG") or (ROOT / "config.yaml")
        with open(p, encoding="utf-8") as f:
            _CFG = yaml.safe_load(f)
    return _CFG


def set_cfg(d):
    global _CFG
    _CFG = d


def out_dir(*parts):
    base = Path(os.environ.get("SA_RUNS") or (ROOT / cfg().get("output_dir", "runs")))
    p = base.joinpath(*parts) if parts else base
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # unique temp name per process/thread: parallel jobs may write the same cache entry at the same time
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, default=str)
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def sha(obj, n=16):
    s = obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def file_sha(path, n=16):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:n]
