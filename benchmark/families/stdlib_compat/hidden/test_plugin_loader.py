import os
import sys
import tempfile

from sa_testlib import case, need


def _write(d, rel, text):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


@case("load_from_path")
def h_load(mod):
    f = need(mod, "load_module_from_path")
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "whatever_file.py", "VALUE = 42\n\ndef hello(name):\n    return 'hi ' + name\n")
        m = f("sa_plugin_alpha", p)
        assert m.VALUE == 42 and m.hello("bob") == "hi bob"
        assert m.__name__ == "sa_plugin_alpha"
        assert sys.modules["sa_plugin_alpha"] is m


@case("load_from_path")
def h_load_new_contents(mod):
    f = need(mod, "load_module_from_path")
    with tempfile.TemporaryDirectory() as d:
        p1 = _write(d, "one.py", "X = 1\n")
        p2 = _write(d, "two.py", "X = 2\nY = 'y'\n")
        assert f("sa_plugin_beta", p1).X == 1
        m = f("sa_plugin_beta", p2)
        assert m.X == 2 and m.Y == "y"
        assert sys.modules["sa_plugin_beta"].X == 2


@case("load_from_path")
def h_load_error_propagates(mod):
    f = need(mod, "load_module_from_path")
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "bad.py", "raise ValueError('broken plugin')\n")
        try:
            f("sa_plugin_bad", p)
        except ValueError as e:
            assert "broken plugin" in str(e)
            return
        raise AssertionError("error while executing the plugin was swallowed")


@case("is_importable")
def h_importable_stdlib(mod):
    f = need(mod, "is_importable")
    assert f("json") is True
    assert f("os.path") is True
    assert f("sa_no_such_module_xyz") is False
    assert f("sa_no_such_pkg_xyz.sub") is False


@case("is_importable")
def h_importable_no_import(mod):
    f = need(mod, "is_importable")
    with tempfile.TemporaryDirectory() as d:
        _write(d, "sa_side_effect_mod.py", "raise RuntimeError('must not be imported')\n")
        sys.path.insert(0, d)
        try:
            assert f("sa_side_effect_mod") is True
            assert "sa_side_effect_mod" not in sys.modules
        finally:
            sys.path.remove(d)


@case("module_file")
def h_module_file_stdlib(mod):
    f = need(mod, "module_file")
    p = f("json")
    assert p is not None and p.endswith(os.path.join("json", "__init__.py")) and os.path.exists(p)
    p2 = f("csv")
    assert p2 is not None and p2.endswith("csv.py")


@case("module_file")
def h_module_file_none(mod):
    f = need(mod, "module_file")
    assert f("sys") is None
    assert f("sa_missing_module_12345") is None


@case("module_file")
def h_module_file_local(mod):
    f = need(mod, "module_file")
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, "sa_local_mod_q.py", "A = 1\n")
        sys.path.insert(0, d)
        try:
            got = f("sa_local_mod_q")
            assert got is not None and os.path.samefile(got, p)
        finally:
            sys.path.remove(d)


@case("list_plugins")
def h_list(mod):
    f = need(mod, "list_plugins")
    with tempfile.TemporaryDirectory() as d:
        _write(d, "gamma.py", "")
        _write(d, "alpha.py", "")
        _write(d, "beta/__init__.py", "")
        _write(d, "notes.txt", "not a module")
        _write(d, "data/readme.md", "no init")
        assert f(d) == ["alpha", "beta", "gamma"]


@case("list_plugins")
def h_list_empty(mod):
    f = need(mod, "list_plugins")
    with tempfile.TemporaryDirectory() as d:
        assert f(d) == []
