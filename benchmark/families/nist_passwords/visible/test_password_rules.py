from sa_testlib import case, need


@case("min_length")
def test_eight_ok(mod):
    assert need(mod, "check_new_password")("abcd1234") == []


@case("blocklist")
def test_blocklisted(mod):
    assert "blocklisted" in need(mod, "check_new_password")("password1", "", ["password1"])


@case("composition")
def test_needs_digit(mod):
    assert "needs_letter_and_digit" in need(mod, "check_new_password")("onlyletters")


@case("username_substring")
def test_username(mod):
    assert "contains_username" in need(mod, "check_new_password")("bob12345xyz", "bob")
