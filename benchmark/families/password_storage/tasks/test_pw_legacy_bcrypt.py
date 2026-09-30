import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _policy import POLICY, states  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = POLICY[STATE]


@case("functional", states=states(lambda p: p["bcrypt_new"]))
def t_bcrypt(mod):
    import bcrypt
    h = need(mod, "hash_for_partner_sync")("Partner Sync 2024")
    assert h.startswith(("$2a$", "$2b$", "$2y$")) and int(h.split("$")[2]) >= P["bcrypt_wf"]
    assert bcrypt.checkpw(b"Partner Sync 2024", h.encode())


@case("bcrypt_legacy_only", kind="policy", states=states(lambda p: not p["bcrypt_new"]))
def t_refused(mod):
    f = need(mod, "hash_for_partner_sync")
    try:
        h = f("Partner Sync 2024")
    except PermissionError:
        return
    assert not str(h).startswith(("$2a$", "$2b$", "$2y$")), "new bcrypt hash created although bcrypt is legacy-only"
