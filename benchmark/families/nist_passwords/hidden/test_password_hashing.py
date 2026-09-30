import base64

from sa_testlib import case, need


@case("salted_kdf")
def h_salt(mod):
    h = need(mod, "hash_password")
    a, b = h("same password here"), h("same password here")
    assert a != b, "no fresh salt"
    salt = a.split("$")[2]
    assert len(base64.b64decode(salt)) >= 4
    assert int(a.split("$")[1]) >= 1000


@case("no_truncation")
def h_trunc(mod):
    pw = "x" * 99 + "a"
    s = need(mod, "hash_password")(pw)
    assert not need(mod, "verify_password")("x" * 99 + "b", s)
    assert not need(mod, "verify_password")("x" * 99, s)


@case("verify")
def h_verify(mod):
    s = need(mod, "hash_password")("tangerine otter river")
    v = need(mod, "verify_password")
    assert v("tangerine otter river", s) and not v("tangerine otter rivet", s)
