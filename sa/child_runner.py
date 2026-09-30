"""Runs test cases against one module inside a target environment.

Invoked as: python -I child_runner.py <module_path|-> <tests_path> <state> <out_json> [<module_name>]
Compatible with Python 3.8+ and has no third-party dependencies."""
import importlib.util
import json
import os
import signal
import sys
import time
import traceback
import types
import warnings

CASES = []
PER_TEST_TIMEOUT = int(os.environ.get("SA_TEST_TIMEOUT", "20"))


def case(component, kind="valid", states="*", weight=1.0):
    def deco(fn):
        CASES.append({"fn": fn, "name": fn.__name__, "component": component, "kind": kind,
                      "states": states, "weight": weight})
        return fn
    return deco


def getfn(mod, name):
    """Return mod.name or None if the module or the function is absent (retired)."""
    if mod is None:
        return None
    return getattr(mod, name, None)


class Missing(Exception):
    pass


def need(mod, name):
    f = getfn(mod, name)
    if f is None:
        raise Missing("function %s is absent from the library" % name)
    return f


def _install_testlib(state):
    lib = types.ModuleType("sa_testlib")
    lib.STATE = state
    lib.case, lib.getfn, lib.need, lib.Missing = case, getfn, need, Missing
    sys.modules["sa_testlib"] = lib


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout("test exceeded %ss" % PER_TEST_TIMEOUT)


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    mod_path, tests_path, state, out = sys.argv[1:5]
    mod_name = sys.argv[5] if len(sys.argv) > 5 else "skill_under_test"
    _install_testlib(state)
    res = {"state": state, "import_error": None, "cases": [], "import_warnings": []}
    mod = None
    if mod_path != "-":
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(mod_path)))
                mod = _load(mod_path, mod_name)
            except BaseException as e:  # noqa
                res["import_error"] = "%s: %s" % (type(e).__name__, str(e)[:500])
                mod = None
            res["import_warnings"] = sorted({"%s: %s" % (x.category.__name__, str(x.message)[:160]) for x in w})
    _load(tests_path, "sa_hidden_tests")
    has_alarm = hasattr(signal, "SIGALRM")
    if has_alarm:
        signal.signal(signal.SIGALRM, _alarm)
    for c in CASES:
        st = c["states"]
        if st != "*" and state not in st:
            continue
        rec = {"name": c["name"], "component": c["component"], "kind": c["kind"], "weight": c["weight"]}
        t0 = time.time()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                if has_alarm:
                    signal.alarm(PER_TEST_TIMEOUT)
                c["fn"](mod)
                rec["passed"], rec["error"] = True, None
            except Missing as e:
                rec["passed"], rec["error"], rec["missing"] = False, str(e), True
            except BaseException as e:  # noqa
                tb = traceback.extract_tb(e.__traceback__)
                where = "%s:%s" % (os.path.basename(tb[-1].filename), tb[-1].lineno) if tb else ""
                rec["passed"], rec["error"] = False, "%s: %s [%s]" % (type(e).__name__, str(e)[:300], where)
            finally:
                if has_alarm:
                    signal.alarm(0)
            rec["warnings"] = sorted({"%s: %s" % (x.category.__name__, str(x.message)[:160]) for x in w})
        rec["seconds"] = round(time.time() - t0, 4)
        res["cases"].append(rec)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f)


if __name__ == "__main__":
    main()
