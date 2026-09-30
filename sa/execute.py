"""Execute test files against a module in a real environment; returns structured results."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import envs

CHILD = Path(__file__).resolve().parent / "child_runner.py"


def run_tests(spec, module_code, tests_path, state, module_name="skill_under_test", timeout=180,
              extra_files=None, tests_src=None):
    """module_code: source string, or None when the skill is absent (retired/removed).
    tests_path: path of a test module; or pass tests_src (source string) instead."""
    py = envs.ensure(spec)
    with tempfile.TemporaryDirectory(prefix="sa_exec_") as td:
        td = Path(td)
        if tests_src is not None:
            tests_path = td / "sa_agent_tests.py"
            tests_path.write_text(tests_src, encoding="utf-8")
        mod_path = "-"
        if module_code is not None:
            mod_path = str(td / f"{module_name}.py")
            Path(mod_path).write_text(module_code, encoding="utf-8")
        for name, content in (extra_files or {}).items():
            (td / name).write_text(content, encoding="utf-8")
        out = td / "result.json"
        env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONHASHSEED"] = "0"
        try:
            r = subprocess.run([py, "-I", str(CHILD), mod_path, str(tests_path), state, str(out), module_name],
                               capture_output=True, text=True, timeout=timeout, cwd=str(td), env=env)
        except subprocess.TimeoutExpired:
            return {"state": state, "fatal": f"timeout after {timeout}s", "cases": []}
        if not out.exists():
            return {"state": state, "fatal": (r.stderr or r.stdout)[-1500:], "cases": []}
        res = json.loads(out.read_text(encoding="utf-8"))
        res["stderr_tail"] = r.stderr[-600:] if r.stderr else ""
        return res
