import base64
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import POLICY  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = POLICY[STATE]


def _pb(digest, it, pw="pw"):
    salt = b"0123456789abcdef"
    dk = hashlib.pbkdf2_hmac(digest, pw.encode(), salt, it)
    return "$pbkdf2-%s$%d$%s$%s" % (digest, it, base64.b64encode(salt).decode().rstrip("="),
                                    base64.b64encode(dk).decode().rstrip("="))


def _sc(ln, pw="pw"):
    salt = b"saltsaltsaltsalt"
    dk = hashlib.scrypt(pw.encode(), salt=salt, n=2 ** ln, r=8, p=1, maxmem=2 ** 29, dklen=32)
    return "$scrypt$ln=%d,r=8,p=1$%s$%s" % (ln, base64.b64encode(salt).decode().rstrip("="),
                                           base64.b64encode(dk).decode().rstrip("="))


def _ar(m, t=2, pw="pw"):
    import argon2
    return argon2.PasswordHasher(time_cost=t, memory_cost=m, parallelism=1).hash(pw)


def _bc(rounds, pw="pw"):
    import bcrypt
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds)).decode()


@case("primary_algorithm")
def h_primary(mod):
    h = need(mod, "hash_new_password")("A long passphrase 42")
    if P["primary"] == "bcrypt":
        assert h.startswith(("$2b$", "$2a$", "$2y$")) and int(h.split("$")[2]) >= P["bcrypt_wf"]
    else:
        assert h.startswith("$argon2id$"), "primary must be Argon2id, got %s" % h[:12]
        m = int(dict(kv.split("=") for kv in h.split("$")[3].split(","))["m"])
        assert m >= P["argon2_m"], "Argon2id memory %d < %d" % (m, P["argon2_m"])
    assert need(mod, "verify_password")("A long passphrase 42", h)


@case("verify_all_formats")
def h_verify_all(mod):
    v = need(mod, "verify_password")
    for enc in (_pb("sha256", 1000), _pb("sha1", 1000), _sc(14), _ar(8192, 1), _bc(10)):
        assert v("pw", enc), enc[:14]
        assert not v("px", enc), enc[:14]


def _expect_rehash():
    """(encoded, expected needs_rehash) pairs derived from the current policy."""
    pairs = [
        (_pb("sha256", 310000), 310000 < P["sha256"]),
        (_pb("sha256", 600000), 600000 < P["sha256"]),
        (_pb("sha512", 210000), 210000 < P["sha512"]),
        (_pb("sha1", 1300000), (1300000 < P["sha1"]) or not P["sha1_new"]),
        (_pb("sha1", 1400000), (1400000 < P["sha1"]) or not P["sha1_new"]),
        (_sc(16), P["scrypt_ln"] is not None and 16 < P["scrypt_ln"]),
        (_sc(17), P["scrypt_ln"] is not None and 17 < P["scrypt_ln"]),
        (_ar(15360), P["argon2_m"] is not None and 15360 < P["argon2_m"]),
        (_ar(19456), P["argon2_m"] is not None and 19456 < P["argon2_m"]),
        (_bc(12), (12 < P["bcrypt_wf"]) or not P["bcrypt_new"]),
        (_bc(10), (10 < P["bcrypt_wf"]) or not P["bcrypt_new"]),
    ]
    return pairs


@case("rehash_thresholds")
def h_rehash(mod):
    f = need(mod, "needs_rehash")
    wrong = [(enc[:22], exp) for enc, exp in _expect_rehash() if bool(f(enc)) != exp]
    assert not wrong, "needs_rehash wrong for %s" % wrong
