import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _policy import POLICY, states  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = POLICY[STATE]


def _it(h):
    return int(h.split("$")[2])


@case("functional")
def t_roundtrip(mod):
    h = need(mod, "fips_password_hash")("fips pass", "sha256")
    assert need(mod, "fips_verify")("fips pass", h) and not need(mod, "fips_verify")("fips pasS", h)


@case("iterations", kind="policy")
def t_iterations(mod):
    f = need(mod, "fips_password_hash")
    assert _it(f("x", "sha256")) >= P["sha256"], "SHA256 iterations below policy"
    assert _it(f("x", "sha512")) >= P["sha512"], "SHA512 iterations below policy"


@case("sha1", kind="policy", states=states(lambda p: p["sha1_new"]))
def t_sha1_ok(mod):
    assert _it(need(mod, "fips_password_hash")("x", "sha1")) >= P["sha1"], "SHA1 iterations below policy"


@case("sha1_legacy_only", kind="policy", states=states(lambda p: not p["sha1_new"]))
def t_sha1_refused(mod):
    f = need(mod, "fips_password_hash")
    try:
        h = f("x", "sha1")
    except (PermissionError, ValueError):
        return
    raise AssertionError("new PBKDF2-HMAC-SHA1 hash created although SHA1 is legacy only")
