from sa_testlib import case, need

EVIL = "x: !!python/object/apply:builtins.len [[1, 2, 3]]\n"


@case("env_substitution")
def h_sub(mod):
    f = need(mod, "load_with_env")
    out = f("db:\n  user: !env DB_USER\n  pw: !env DB_PW\n", {"DB_USER": "svc", "DB_PW": "s3"})
    assert out == {"db": {"user": "svc", "pw": "s3"}}


@case("env_substitution")
def h_isolated_calls(mod):
    f = need(mod, "load_with_env")
    assert f("u: !env A\n", {"A": "1"}) == {"u": "1"}
    assert f("u: !env A\n", {"A": "2"}) == {"u": "2"}


@case("env_default")
def h_default(mod):
    f = need(mod, "load_with_env")
    assert f("host: !env HOST:localhost\n", {}) == {"host": "localhost"}
    assert f("host: !env HOST:localhost\n", {"HOST": "db"}) == {"host": "db"}


@case("plain_values")
def h_plain(mod):
    f = need(mod, "load_with_env")
    assert f("a: 1\nb: [x, y]\nc: {d: true}\n", {}) == {"a": 1, "b": ["x", "y"], "c": {"d": True}}


@case("no_object_construction", kind="policy")
def h_no_apply(mod):
    f = need(mod, "load_with_env")
    try:
        out = f(EVIL, {})
    except Exception:
        return
    assert out.get("x") != 3, "arbitrary Python object constructed from YAML"
