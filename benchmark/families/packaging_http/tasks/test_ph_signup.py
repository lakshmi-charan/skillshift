from sa_testlib import case, need


def _messages(f, data):
    try:
        f(data)
    except ValueError as e:
        return e.messages
    raise AssertionError("expected ValueError for %r" % (data,))


@case("functional")
def t_valid(mod):
    f = need(mod, "validate_signup")
    assert f({"username": "neo", "email": "neo@example.com", "ref": "x"}) == \
        {"username": "neo", "email": "neo@example.com", "plan": "free"}
    assert f({"username": "trin1", "email": "t@example.com", "plan": "pro", "age": 16})["age"] == 16


@case("functional")
def t_invalid(mod):
    f = need(mod, "validate_signup")
    m = _messages(f, {"username": "bad name", "email": "nope", "plan": "gold", "age": 12})
    assert set(m) == {"username", "email", "plan", "age"}, m
    assert all(isinstance(v, list) and v for v in m.values())
    assert set(_messages(f, {"email": "a@example.com"})) == {"username"}
    assert set(_messages(f, {"username": "ok", "email": "a@example.com", "age": 121})) == {"age"}
