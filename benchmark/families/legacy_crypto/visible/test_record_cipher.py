from sa_testlib import case, need


@case("roundtrip")
def test_rt(mod):
    k = bytes(32)
    assert need(mod, "decrypt_record")(k, need(mod, "encrypt_record")(k, b"r", b"a"), b"a") == b"r"
