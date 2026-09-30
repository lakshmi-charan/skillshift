from sa_testlib import case, need

K = bytes(range(1, 25))


@case("tdes_encrypt")
def test_roundtrip(mod):
    blob = need(mod, "encrypt_for_partner")(K, b"hello partner")
    assert need(mod, "decrypt_payload")(K, blob) == b"hello partner"
    assert len(blob) % 8 == 0 and len(blob) >= 16
