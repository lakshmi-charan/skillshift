import pydantic
from sa_testlib import case, need

GOOD = {"username": "bob", "email": "bob@example.com", "phone": "+1 555 010 9999",
        "password": "hunter2hunter2", "password_confirm": "hunter2hunter2"}


@case("phone_normalised")
def test_valid(mod):
    assert need(mod, "parse_signup")(GOOD).phone == "+15550109999"


@case("username_pattern")
def test_bad_username(mod):
    try:
        need(mod, "parse_signup")(dict(GOOD, username="Bob!"))
    except pydantic.ValidationError as e:
        assert e.errors()[0]["type"] == "value_error.str.regex"
        return
    raise AssertionError("expected ValidationError")


@case("passwords_match")
def test_mismatch(mod):
    try:
        need(mod, "parse_signup")(dict(GOOD, password_confirm="nope-nope"))
    except pydantic.ValidationError as e:
        assert "passwords do not match" in str(e)
        return
    raise AssertionError("expected ValidationError")
