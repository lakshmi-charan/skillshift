import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import POLICY, ALL, states, refused  # noqa: E402
from sa_testlib import case, need, getfn, STATE  # noqa: E402

P = POLICY[STATE]


def _parse(h):
    _, scheme, it, salt, dk = h.split("$")
    return scheme, int(it), salt, dk


@case("sha256_iterations")
def h_sha256(mod):
    scheme, it, _, _ = _parse(need(mod, "hash_pbkdf2")("correct horse", "sha256"))
    assert scheme == "pbkdf2-sha256" and it >= P["sha256"], "iterations %d < %d" % (it, P["sha256"])


@case("sha512_iterations")
def h_sha512(mod):
    scheme, it, _, _ = _parse(need(mod, "hash_pbkdf2")("correct horse", "sha512"))
    assert scheme == "pbkdf2-sha512" and it >= P["sha512"], "iterations %d < %d" % (it, P["sha512"])


@case("sha1_new_hashes", states=states(lambda p: p["sha1_new"]))
def h_sha1(mod):
    scheme, it, _, _ = _parse(need(mod, "hash_pbkdf2")("correct horse", "sha1"))
    assert scheme == "pbkdf2-sha1" and it >= P["sha1"], "iterations %d < %d" % (it, P["sha1"])


@case("sha1_new_hashes", kind="obsolete", states=states(lambda p: not p["sha1_new"]))
def o_sha1_refused(mod):
    assert refused(getfn(mod, "hash_pbkdf2"), "correct horse", "sha1"), "new PBKDF2-HMAC-SHA1 hash created"


@case("salt")
def h_salt(mod):
    import base64
    f = need(mod, "hash_pbkdf2")
    a, b = f("pw-one-two", "sha256"), f("pw-one-two", "sha256")
    sa = _parse(a)[2]
    assert a != b and len(base64.b64decode(sa + "=" * (-len(sa) % 4))) >= 16


@case("verify")
def h_verify_roundtrip(mod):
    h = need(mod, "hash_pbkdf2")("Tr0ub4dor&3", "sha256")
    v = need(mod, "verify_pbkdf2")
    assert v("Tr0ub4dor&3", h) and not v("Tr0ub4dor&4", h)


@case("verify")
def h_verify_legacy(mod):
    import base64
    import hashlib
    v = need(mod, "verify_pbkdf2")
    for digest, it in (("sha1", 1000), ("sha256", 10000), ("sha512", 5000)):
        salt = b"0123456789abcdef"
        dk = hashlib.pbkdf2_hmac(digest, "legacy-pw".encode(), salt, it)
        enc = "$pbkdf2-%s$%d$%s$%s" % (digest, it, base64.b64encode(salt).decode().rstrip("="),
                                       base64.b64encode(dk).decode().rstrip("="))
        assert v("legacy-pw", enc) and not v("legacy-px", enc), digest
