import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import POLICY, states  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = POLICY[STATE]


def _params(h):
    parts = h.split("$")
    assert parts[1] == "scrypt"
    return {k: int(v) for k, v in (kv.split("=") for kv in parts[2].split(","))}


@case("cost_parameter", states=states(lambda p: p["scrypt_ln"] is not None))
def h_cost(mod):
    p = _params(need(mod, "hash_scrypt")("pw"))
    assert p["ln"] >= P["scrypt_ln"] and p["r"] == 8 and p["p"] == 1, p


@case("cost_parameter")
def h_runs(mod):
    h = need(mod, "hash_scrypt")("another pw")
    assert h.startswith("$scrypt$")


@case("verify")
def h_verify(mod):
    h = need(mod, "hash_scrypt")("scrypt me")
    v = need(mod, "verify_scrypt")
    assert v("scrypt me", h) and not v("scrypt mE", h)


@case("verify")
def h_verify_legacy(mod):
    import base64
    import hashlib
    salt = b"saltsaltsaltsalt"
    dk = hashlib.scrypt(b"legacy", salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    enc = "$scrypt$ln=14,r=8,p=1$%s$%s" % (base64.b64encode(salt).decode().rstrip("="),
                                           base64.b64encode(dk).decode().rstrip("="))
    v = need(mod, "verify_scrypt")
    assert v("legacy", enc) and not v("legacx", enc)
