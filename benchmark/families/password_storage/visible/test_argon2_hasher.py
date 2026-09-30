from sa_testlib import case, need


@case("memory_cost")
def test_params(mod):
    assert "$m=15360,t=2,p=1$" in need(mod, "hash_argon2")("pw")


@case("verify")
def test_roundtrip(mod):
    h = need(mod, "hash_argon2")("pw")
    assert need(mod, "verify_argon2")("pw", h)
