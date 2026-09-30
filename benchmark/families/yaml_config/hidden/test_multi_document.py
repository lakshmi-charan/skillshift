from sa_testlib import case, need

EVIL = "a: 1\n---\nx: !!python/object/apply:builtins.len [[1, 2, 3]]\n"


@case("split_documents")
def h_three(mod):
    f = need(mod, "load_all_documents")
    assert f("a: 1\n---\n- x\n- y\n---\nplain\n") == [{"a": 1}, ["x", "y"], "plain"]


@case("split_documents")
def h_single(mod):
    assert need(mod, "load_all_documents")("k: v\n") == [{"k": "v"}]


@case("skip_empty")
def h_empty_docs(mod):
    assert need(mod, "load_all_documents")("---\na: 1\n---\n---\nb: 2\n") == [{"a": 1}, {"b": 2}]


@case("no_object_construction", kind="policy")
def h_no_apply(mod):
    f = need(mod, "load_all_documents")
    try:
        out = f(EVIL)
    except Exception:
        return
    assert all(not (isinstance(d, dict) and d.get("x") == 3) for d in out), "arbitrary object constructed"
