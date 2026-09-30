from sa_testlib import case, need

BASE = {"username": "alice", "email": "alice@example.com"}


def _err(fn, *args):
    E = None
    try:
        fn(*args)
    except ValueError as e:
        E = e
    assert E is not None, "expected a ValueError (UserError)"
    assert hasattr(E, "messages"), "error must carry field messages"
    return E.messages


@case("load_defaults")
def h_load_defaults(mod):
    f = need(mod, "load_user")
    out = f(dict(BASE))
    assert out == {"username": "alice", "email": "alice@example.com", "role": "member", "tags": []}


@case("load_defaults")
def h_load_defaults_fresh_list(mod):
    f = need(mod, "load_user")
    a, b = f(dict(BASE)), f(dict(BASE))
    a["tags"].append("x")
    assert b["tags"] == []
    assert f(dict(BASE, role="admin", tags=["ops"]))["role"] == "admin"


@case("load_defaults")
def h_unknown_dropped(mod):
    f = need(mod, "load_user")
    out = f(dict(BASE, is_superuser=True, age=30))
    assert "is_superuser" not in out and out["age"] == 30


@case("dump_defaults")
def h_dump_defaults(mod):
    f = need(mod, "dump_user")
    out = f({"username": "bob", "email": "bob@example.com", "role": "member"})
    assert out["active"] is True and out["username"] == "bob"
    assert "age" not in out


@case("dump_defaults")
def h_dump_explicit(mod):
    f = need(mod, "dump_user")
    out = f({"username": "bob", "email": "bob@example.com", "active": False, "age": 40, "tags": ["a"]})
    assert out["active"] is False and out["age"] == 40 and out["tags"] == ["a"]


@case("validation")
def h_age_range(mod):
    f = need(mod, "load_user")
    assert f(dict(BASE, age=13))["age"] == 13
    assert "age" in _err(f, dict(BASE, age=5))
    assert "age" in _err(f, dict(BASE, age=200))


@case("validation")
def h_username_email(mod):
    f = need(mod, "load_user")
    m = _err(f, {"username": "bob smith", "email": "not-an-email"})
    assert "username" in m and "email" in m


@case("validation")
def h_required(mod):
    f = need(mod, "load_user")
    m = _err(f, {"email": "x@example.com"})
    assert "username" in m


@case("batch_load")
def h_batch_list(mod):
    f = need(mod, "load_users")
    out = f([dict(BASE), {"username": "bob", "email": "bob@example.com", "role": "admin"}])
    assert [u["username"] for u in out] == ["alice", "bob"]
    assert out[0]["role"] == "member" and out[1]["role"] == "admin"


@case("batch_load")
def h_batch_envelope(mod):
    f = need(mod, "load_users")
    out = f({"users": [dict(BASE)]})
    assert out == [{"username": "alice", "email": "alice@example.com", "role": "member", "tags": []}]


@case("batch_load")
def h_batch_error(mod):
    f = need(mod, "load_users")
    m = _err(f, {"users": [dict(BASE), {"username": "x y", "email": "y@example.com"}]})
    assert 1 in m and "username" in m[1]
