from sa_testlib import case, need


@case("work_factor")
def test_rounds_12(mod):
    assert need(mod, "hash_bcrypt")("pw").split("$")[2] == "12"


@case("input_limit")
def test_65_chars_rejected(mod):
    try:
        need(mod, "hash_bcrypt")("x" * 65)
    except ValueError:
        return
    raise AssertionError("65-character password accepted")


@case("verify")
def test_roundtrip(mod):
    h = need(mod, "hash_bcrypt")("pw")
    assert need(mod, "verify_bcrypt")("pw", h)
