from sa_testlib import case, need, STATE

MIN = {"s0": 8, "s1": 15}[STATE]


def r(mod, u, p, b=()):
    return list(need(mod, "validate_signup")(u, p, set(b)))


@case("functional")
def t_length(mod):
    assert "too_short" in r(mod, "zed", ("k7" + "abcdefghijklmnop")[: MIN - 1])
    assert "too_short" not in r(mod, "zed", ("k7" + "abcdefghijklmnop")[:MIN])


@case("functional")
def t_breached(mod):
    assert "blocklisted" in r(mod, "zed", "sunshine-4-lollipop", {"sunshine-4-lollipop"})


@case("functional")
def t_username_equal(mod):
    assert "contains_username" in r(mod, "harriet.jones.1984", "Harriet.Jones.1984")


@case("functional")
def t_good(mod):
    assert r(mod, "zed", "velvet 7 thunder orchard") == []


@case("org_rules", states=["s0"])
def t_org_rules_s0(mod):
    assert "needs_letter_and_digit" in r(mod, "zed", "velvetthunderorchard")
    assert "contains_username" in r(mod, "alice", "alice-likes-green-tea-42")


@case("prohibited_rules", kind="policy", states=["s1"])
def t_no_composition_or_substring(mod):
    assert r(mod, "zed", "velvetthunderorchard") == [], "composition rule applied"
    assert "contains_username" not in r(mod, "alice", "alice-likes-green-tea-42"), "substring rejection applied"
