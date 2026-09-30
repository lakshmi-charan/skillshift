from sa_testlib import case, need


@case("primary_algorithm")
def test_new_hash_is_bcrypt(mod):
    h = need(mod, "hash_new_password")("pw")
    assert h.startswith("$2b$12$") and need(mod, "verify_password")("pw", h)


@case("rehash_thresholds")
def test_weak_pbkdf2_rehashed(mod):
    import base64
    import hashlib
    dk = hashlib.pbkdf2_hmac("sha256", b"pw", b"s" * 16, 1000)
    enc = "$pbkdf2-sha256$1000$%s$%s" % (base64.b64encode(b"s" * 16).decode().rstrip("="),
                                        base64.b64encode(dk).decode().rstrip("="))
    assert need(mod, "needs_rehash")(enc) is True
