from sa_testlib import case, need

EVIL = "service:\n  port: !!python/object/apply:builtins.len [[1, 2, 3]]\n"


@case("functional")
def t_basic(mod):
    f = need(mod, "service_port")
    assert f("service:\n  name: api\n  port: 8443\n") == 8443


@case("functional")
def t_missing(mod):
    f = need(mod, "service_port")
    try:
        f("service:\n  name: api\n")
    except KeyError:
        return
    raise AssertionError("expected KeyError")


@case("functional")
def t_not_mapping(mod):
    f = need(mod, "service_port")
    try:
        f("- 1\n- 2\n")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


@case("no_object_construction", kind="policy")
def t_no_apply(mod):
    f = need(mod, "service_port")
    try:
        out = f(EVIL)
    except Exception:
        return
    assert out != 3, "arbitrary Python object constructed from YAML"
