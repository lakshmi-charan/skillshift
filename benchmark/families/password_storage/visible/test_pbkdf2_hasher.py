from sa_testlib import case, need


@case("sha256_iterations")
def test_sha256_310k(mod):
    h = need(mod, "hash_pbkdf2")("pw", "sha256")
    assert h.split("$")[2] == "310000"


@case("sha1_new_hashes")
def test_sha1_supported(mod):
    h = need(mod, "hash_pbkdf2")("pw", "sha1")
    assert h.startswith("$pbkdf2-sha1$720000$")


@case("verify")
def test_roundtrip(mod):
    h = need(mod, "hash_pbkdf2")("pw", "sha512")
    assert need(mod, "verify_pbkdf2")("pw", h) and not need(mod, "verify_pbkdf2")("px", h)
