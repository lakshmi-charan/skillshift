import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _util import raises_value_error  # noqa: E402
from sa_testlib import case, need  # noqa: E402

GOOD = {"username": "ann_42", "email": "ann@example.com", "phone": "+44 20 7946 0958",
        "password": "correct horse", "password_confirm": "correct horse"}


def _with(**kw):
    d = dict(GOOD)
    d.update(kw)
    return d


@case("username_pattern")
def h_username_ok(mod):
    f = need(mod, "parse_signup")
    assert f(GOOD).username == "ann_42"
    assert f(_with(username="abc")).username == "abc"
    assert f(_with(username="a" * 20)).username == "a" * 20


@case("username_pattern")
def h_username_rejected(mod):
    f = need(mod, "parse_signup")
    for bad in ("ab", "a" * 21, "Ann", "ann-42", "ann 42", "anné"):
        assert raises_value_error(f, _with(username=bad)), bad


@case("passwords_match")
def h_passwords_match(mod):
    f = need(mod, "parse_signup")
    form = f(GOOD)
    assert form.password == form.password_confirm == "correct horse"
    assert raises_value_error(f, _with(password_confirm="correct horsE"))


@case("passwords_match")
def h_passwords_length(mod):
    f = need(mod, "parse_signup")
    assert raises_value_error(f, _with(password="short", password_confirm="short"))
    assert raises_value_error(f, _with(password="short", password_confirm="different1"))
    assert f(_with(password="12345678", password_confirm="12345678")).password == "12345678"


@case("phone_normalised")
def h_phone_normalised(mod):
    f = need(mod, "parse_signup")
    assert f(GOOD).phone == "+442079460958"
    assert f(_with(phone="+1 (555) 010-9999")).phone == "+15550109999"
    assert f(_with(phone="+49.30.1234567")).phone == "+49301234567"


@case("phone_normalised")
def h_phone_rejected(mod):
    f = need(mod, "parse_signup")
    for bad in ("020 7946 0958", "+123", "+1234567890123456", "+44 20 79x6 0958", 4420794609):
        assert raises_value_error(f, _with(phone=bad)), bad
