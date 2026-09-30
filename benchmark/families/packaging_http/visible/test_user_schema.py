from sa_testlib import case, need


@case("load_defaults")
def test_role_default(mod):
    assert need(mod, "load_user")({"username": "amy", "email": "amy@example.com"})["role"] == "member"


@case("dump_defaults")
def test_active_default(mod):
    assert need(mod, "dump_user")({"username": "amy", "email": "amy@example.com"})["active"] is True


@case("validation")
def test_too_young(mod):
    try:
        need(mod, "load_user")({"username": "kid", "email": "k@example.com", "age": 8})
    except ValueError as e:
        assert e.messages == {"age": ["Invalid value."]}
        return
    raise AssertionError("expected UserError")
