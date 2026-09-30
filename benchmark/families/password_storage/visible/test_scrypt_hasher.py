from sa_testlib import case, need


@case("cost_parameter")
def test_params(mod):
    assert need(mod, "hash_scrypt")("pw").startswith("$scrypt$ln=16,r=8,p=1$")


@case("verify")
def test_roundtrip(mod):
    h = need(mod, "hash_scrypt")("pw")
    assert need(mod, "verify_scrypt")("pw", h)
