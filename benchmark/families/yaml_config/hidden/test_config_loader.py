import os
import tempfile

from sa_testlib import case, need

EVIL = "x: !!python/object/apply:builtins.len [[1, 2, 3]]\n"


@case("parse_mapping")
def h_nested(mod):
    f = need(mod, "load_config_text")
    out = f("app:\n  name: demo\n  debug: true\n  ratio: 0.5\n  tags: [a, b]\n")
    assert out == {"app": {"name": "demo", "debug": True, "ratio": 0.5, "tags": ["a", "b"]}}


@case("parse_mapping")
def h_types(mod):
    out = need(mod, "load_config_text")("n: 3\nnone: null\nwhen: 2021-05-01\n")
    assert out["n"] == 3 and out["none"] is None and str(out["when"]) == "2021-05-01"


@case("empty_document")
def h_empty(mod):
    f = need(mod, "load_config_text")
    assert f("") == {} and f("# only a comment\n") == {}


@case("reject_non_mapping")
def h_scalar(mod):
    f = need(mod, "load_config_text")
    for bad in ("42\n", "- 1\n- 2\n", "just text\n"):
        try:
            f(bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError for %r" % bad)


@case("file_loading")
def h_file(mod):
    f = need(mod, "load_config_file")
    fd, p = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("name: café\nport: 8080\n")
    try:
        assert f(p) == {"name": "café", "port": 8080}
    finally:
        os.remove(p)


@case("no_object_construction", kind="policy")
def h_no_apply(mod):
    f = need(mod, "load_config_text")
    try:
        out = f(EVIL)
    except Exception:
        return
    assert out.get("x") != 3, "arbitrary Python object constructed from YAML"
