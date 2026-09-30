from sa_testlib import case, need

GOOD = {"username": "zoe_1", "email": "  Zoe@Example.COM ", "phone": "+33 (0)1 23.45.67.89",
        "password": "longenough", "password_confirm": "longenough"}


def _rejects(f, data):
    try:
        f(data)
    except ValueError:
        return True
    return False


@case("functional")
def t_valid(mod):
    f = need(mod, "validate_signup")
    assert f(GOOD) == {"username": "zoe_1", "email": "zoe@example.com", "phone": "+330123456789"}


@case("functional")
def t_invalid(mod):
    f = need(mod, "validate_signup")
    bad = [dict(GOOD, username="Zo"), dict(GOOD, username="zoe!"), dict(GOOD, email="zoe.example.com"),
           dict(GOOD, phone="0123456789"), dict(GOOD, phone=33123456789),
           dict(GOOD, password="short", password_confirm="short"), dict(GOOD, password_confirm="longenougH")]
    missing = dict(GOOD)
    del missing["phone"]
    bad.append(missing)
    for d in bad:
        assert _rejects(f, d), d
