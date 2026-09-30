from sa_testlib import case, need, getfn, STATE

MIN = {"s0": 8, "s1": 15}[STATE]


def _reasons(mod, pw, user="", bl=()):
    return list(need(mod, "check_new_password")(pw, user, bl))


@case("min_length")
def h_too_short(mod):
    pw = ("k7" + "abcdefghijklmnop")[: MIN - 1]
    assert "too_short" in _reasons(mod, pw), "password of %d chars not rejected" % (MIN - 1)


@case("min_length")
def h_min_ok(mod):
    pw = ("k7" + "abcdefghijklmnop")[:MIN]
    assert "too_short" not in _reasons(mod, pw), "password of exactly %d chars rejected as too short" % MIN


@case("code_point_length")
def h_code_points(mod):
    ok = "é" * (MIN - 1) + "1"          # MIN code points, more bytes
    short = "é" * (MIN - 2) + "1"
    assert "too_short" not in _reasons(mod, ok)
    assert "too_short" in _reasons(mod, short)


@case("code_point_length")
def h_emoji(mod):
    pw = "\U0001F511" * (MIN - 2) + "a1"
    assert "too_short" not in _reasons(mod, pw)


@case("long_passwords")
def h_long(mod):
    for n in (64, 100, 256):
        pw = ("k7" + "horse battery staple " * 20)[:n]
        assert _reasons(mod, pw) == [], "password of %d chars rejected: %s" % (n, _reasons(mod, pw))


@case("blocklist")
def h_blocklist(mod):
    bl = ["correcthorsebatterystaple1", "password1234567890"]
    assert "blocklisted" in _reasons(mod, "correcthorsebatterystaple1", "", bl)
    assert "blocklisted" in _reasons(mod, "password1234567890", "", bl)


@case("blocklist")
def h_not_blocklisted(mod):
    bl = ["correcthorsebatterystaple1"]
    assert "blocklisted" not in _reasons(mod, "tangerine-otter-river-42", "", bl)


@case("username_exact")
def h_username_equal(mod):
    assert "contains_username" in _reasons(mod, "LongUsername2020ABC", "longusername2020abc")


@case("username_substring", states=["s0"])
def h_username_substring(mod):
    assert "contains_username" in _reasons(mod, "alice-likes-green-tea-42", "alice")


@case("username_substring", kind="obsolete", states=["s1"])
def o_username_substring(mod):
    f = getfn(mod, "check_new_password")
    if f is None:
        return
    r = list(f("alice-likes-green-tea-42", "alice", ()))
    assert "contains_username" not in r, "rejected because a substring matches the username"


@case("composition", states=["s0"])
def h_composition(mod):
    assert "needs_letter_and_digit" in _reasons(mod, "correcthorsebatterystaple")
    assert "needs_letter_and_digit" in _reasons(mod, "12345678901234567890")
    assert "needs_letter_and_digit" not in _reasons(mod, "correcthorse9batterystaple")


@case("composition", kind="obsolete", states=["s1"])
def o_composition(mod):
    f = getfn(mod, "check_new_password")
    if f is None:
        return
    for pw in ("correcthorsebatterystaple", "12345678901234567890", "tangerine otter river"):
        r = list(f(pw, "", ()))
        assert r == [], "composition rule applied to %r: %s" % (pw, r)
