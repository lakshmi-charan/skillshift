import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import POLICY, states, refused  # noqa: E402
from sa_testlib import case, need, getfn, STATE  # noqa: E402

P = POLICY[STATE]
NEW_OK = states(lambda p: p["bcrypt_new"])


@case("work_factor", states=NEW_OK)
def h_wf(mod):
    h = need(mod, "hash_bcrypt")("pw")
    assert int(h.split("$")[2]) >= P["bcrypt_wf"]


@case("input_limit", states=NEW_OK)
def h_limit(mod):
    f = need(mod, "hash_bcrypt")
    kind, n = P["bcrypt_limit"]
    if kind == "chars":
        f("a" * n)
        try:
            f("a" * (n + 1))
        except ValueError:
            return
        raise AssertionError("over-long password accepted")
    # bytes: every password up to 72 bytes must hash; anything longer must be rejected (no silent truncation)
    f("a" * 72)
    for bad in ("a" * 73, "€" * 30):
        try:
            f(bad)
        except ValueError:
            continue
        raise AssertionError("password of %d bytes accepted (bcrypt would truncate)" % len(bad.encode()))


@case("new_hashes_permitted", kind="obsolete", states=states(lambda p: not p["bcrypt_new"]))
def o_no_new_bcrypt(mod):
    assert refused(getfn(mod, "hash_bcrypt"), "pw"), "new bcrypt hash created although bcrypt is legacy-only"


@case("verify")
def h_verify(mod):
    import bcrypt
    old = bcrypt.hashpw(b"legacy pw", bcrypt.gensalt(10)).decode()
    v = need(mod, "verify_bcrypt")
    assert v("legacy pw", old) and not v("legacy pX", old)
