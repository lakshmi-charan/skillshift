"""Isolated real-software environments (one uv virtualenv per {python, packages} spec)."""
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from .common import ROOT, sha, write_json, read_json

_LOCKS = {}
_GLOBAL = threading.Lock()


# Exact interpreter builds (python-build-standalone via uv 0.12.21). Pinning the patch release also pins the
# bundled OpenSSL, which matters for the TLS family.
PY_PINS = {"3.9": "3.9.25", "3.10": "3.10.21", "3.11": "3.11.16", "3.12": "3.12.14", "3.13": "3.13.15",
           "3.14": "3.14.7"}


EXCLUDE_NEWER = "2026-09-30T00:00:00Z"


def pinned(py):
    return PY_PINS.get(str(py), str(py))


def uv_bin():
    return os.environ.get("SA_UV") or shutil.which("uv") or "uv"


def env_root():
    p = Path(os.environ.get("SA_ENVS") or (ROOT / "envs"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def spec_key(spec):
    pk = {k: str(v) for k, v in sorted((spec.get("packages") or {}).items())}
    py = pinned(spec["python"])
    return "py" + py.replace(".", "") + "-" + sha({"python": py, "packages": pk}, 10)


def _req(name, ver):
    ver = str(ver)
    if any(ver.startswith(op) for op in ("<", ">", "=", "!", "~")):
        return f"{name}{ver}"
    return f"{name}=={ver}"


class _file_lock:
    """Cross-process lock (POSIX fcntl; no-op elsewhere) so parallel runs never build the same env twice."""

    def __init__(self, path):
        self.path = path
        self.fh = None

    def __enter__(self):
        try:
            import fcntl
            self.fh = open(self.path, "w")
            fcntl.flock(self.fh, fcntl.LOCK_EX)
        except ImportError:
            self.fh = None
        return self

    def __exit__(self, *a):
        if self.fh is not None:
            import fcntl
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()


def ensure(spec):
    """Create (once) and return the python executable for this environment spec."""
    key = spec_key(spec)
    with _GLOBAL:
        lock = _LOCKS.setdefault(key, threading.Lock())
    with lock, _file_lock(env_root() / f".{key}.lock"):
        d = env_root() / key
        py = d / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        marker = d / "sa_env.json"
        if marker.exists() and py.exists():
            return str(py)
        if d.exists():
            shutil.rmtree(d)
        uv = uv_bin()
        r = subprocess.run([uv, "venv", "-q", "--python-preference", "only-managed", "-p", pinned(spec["python"]),
                            str(d)], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"uv venv failed for {key}: {r.stderr[-800:]}")
        reqs = [_req(k, v) for k, v in (spec.get("packages") or {}).items()]
        if reqs:
            envv = dict(os.environ, VIRTUAL_ENV=str(d))
            pin_date = ["--exclude-newer", EXCLUDE_NEWER]   # freeze transitive dependencies for reproducibility
            r = subprocess.run([uv, "pip", "install", "-q", *pin_date, "--only-binary", ":all:", *reqs],
                               capture_output=True, text=True, env=envv)
            if r.returncode != 0:
                r = subprocess.run([uv, "pip", "install", "-q", *pin_date, *reqs], capture_output=True, text=True,
                                   env=envv)
            if r.returncode != 0:
                shutil.rmtree(d, ignore_errors=True)
                raise RuntimeError(f"uv pip install failed for {key} {reqs}: {r.stderr[-800:]}")
        # record exact resolved versions for the reproducibility appendix
        fr = subprocess.run([str(py), "-c", "import sys,json,importlib.metadata as m;"
                             "print(json.dumps({'python':sys.version.split()[0],"
                             "'packages':{d.metadata['Name'].lower():d.version for d in m.distributions()}}))"],
                            capture_output=True, text=True)
        info = {"spec": spec, "key": key}
        try:
            import json
            info.update(json.loads(fr.stdout))
        except Exception:
            info["freeze_error"] = fr.stderr[-400:]
        write_json(marker, info)
        return str(py)


def info(spec):
    ensure(spec)
    return read_json(env_root() / spec_key(spec) / "sa_env.json")
