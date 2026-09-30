import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import POLICY, states  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = POLICY[STATE]


def _params(h):
    parts = h.split("$")
    assert parts[1] == "argon2id", "not Argon2id: %s" % parts[1]
    return {k: int(v) for k, v in (kv.split("=") for kv in parts[3].split(","))}


@case("memory_cost", states=states(lambda p: p["argon2_m"] is not None))
def h_memory(mod):
    m = _params(need(mod, "hash_argon2")("pw"))["m"]
    assert m >= P["argon2_m"], "memory %d KiB < %d KiB" % (m, P["argon2_m"])


@case("time_parallelism")
def h_tp(mod):
    p = _params(need(mod, "hash_argon2")("pw"))
    assert p["t"] >= 2 and p["p"] == 1


@case("verify")
def h_verify(mod):
    h = need(mod, "hash_argon2")("s3cret pass")
    v = need(mod, "verify_argon2")
    assert v("s3cret pass", h) and not v("s3cret pasz", h)


@case("verify")
def h_verify_legacy(mod):
    import argon2
    old = argon2.PasswordHasher(time_cost=1, memory_cost=8192, parallelism=2).hash("old one")
    v = need(mod, "verify_argon2")
    assert v("old one", old) and not v("old two", old)
