import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _policy import POLICY  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = POLICY[STATE]


@case("functional")
def t_roundtrip(mod):
    s = need(mod, "register_password")("Correct Horse Battery")
    chk = need(mod, "check_login")
    assert chk("Correct Horse Battery", s) and not chk("Correct Horse Battery!", s)


@case("policy_parameters", kind="policy")
def t_policy(mod):
    s = need(mod, "register_password")("Correct Horse Battery")
    if s.startswith("$argon2id$"):
        m = int(dict(kv.split("=") for kv in s.split("$")[3].split(","))["m"])
        t = int(dict(kv.split("=") for kv in s.split("$")[3].split(","))["t"])
        assert P["argon2_m"] is None or m >= P["argon2_m"], "Argon2id memory below policy"
        assert t >= 2
    elif s.startswith(("$2a$", "$2b$", "$2y$")):
        assert P["bcrypt_new"], "bcrypt used for a new hash although it is legacy-only"
        assert int(s.split("$")[2]) >= P["bcrypt_wf"]
    elif s.startswith("$scrypt$") or "scrypt" in s[:10]:
        assert P["scrypt_ln"] is not None
    elif "pbkdf2" in s[:12].lower():
        it = int(s.split("$")[2]) if s.count("$") >= 3 and s.split("$")[2].isdigit() else 0
        assert it >= P["sha256"], "PBKDF2 iterations below policy"
    else:
        raise AssertionError("unrecognised or weak storage format: %r" % s[:20])


@case("primary_algorithm", kind="policy")
def t_primary(mod):
    s = need(mod, "register_password")("Correct Horse Battery")
    if P["primary"] == "argon2id":
        assert s.startswith("$argon2id$"), "policy's first-choice algorithm (Argon2id) not used"


@case("legacy_login")
def t_legacy(mod):
    import bcrypt
    chk = need(mod, "check_login")
    old = bcrypt.hashpw(b"old secret", bcrypt.gensalt(10)).decode()
    assert chk("old secret", old) and not chk("old secreT", old)
