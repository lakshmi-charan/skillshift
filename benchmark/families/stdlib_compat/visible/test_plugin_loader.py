import os
import tempfile

from sa_testlib import case, need


@case("load_from_path")
def test_load(mod):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "plug.py")
        with open(p, "w") as fh:
            fh.write("NAME = 'demo'\n")
        assert need(mod, "load_module_from_path")("demo_plug", p).NAME == "demo"


@case("is_importable")
def test_importable(mod):
    assert need(mod, "is_importable")("json") and not need(mod, "is_importable")("no_such_mod_abc")


@case("list_plugins")
def test_list(mod):
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.py"), "w").close()
        assert need(mod, "list_plugins")(d) == ["a"]
