from sa_testlib import case, need

K = bytes(range(32))


@case("roundtrip")
def h_rt(mod):
    e, d = need(mod, "encrypt_record"), need(mod, "decrypt_record")
    assert d(K, e(K, b"patient 7; result negative", b"hdr"), b"hdr") == b"patient 7; result negative"


@case("roundtrip")
def h_nonce(mod):
    e = need(mod, "encrypt_record")
    assert e(K, b"x") != e(K, b"x")


@case("tamper_detection")
def h_tamper(mod):
    e, d = need(mod, "encrypt_record"), need(mod, "decrypt_record")
    blob = bytearray(e(K, b"payload", b"a"))
    blob[-1] ^= 1
    for bad, aad in ((bytes(blob), b"a"), (e(K, b"payload", b"a"), b"b")):
        try:
            d(K, bad, aad)
        except Exception:
            continue
        raise AssertionError("tampering not detected")
