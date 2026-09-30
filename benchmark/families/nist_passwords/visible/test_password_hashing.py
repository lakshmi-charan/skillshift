from sa_testlib import case, need


@case("verify")
def test_roundtrip(mod):
    s = need(mod, "hash_password")("pw12345678")
    assert need(mod, "verify_password")("pw12345678", s)
