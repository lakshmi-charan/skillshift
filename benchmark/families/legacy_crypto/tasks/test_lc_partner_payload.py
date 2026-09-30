import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _crypto_helpers import KEY24, tdes_decrypt_ref  # noqa: E402
from sa_testlib import case, need  # noqa: E402


@case("functional", states=["s0"])
def t_ok(mod):
    blob = need(mod, "build_partner_payload")(KEY24, b"settlement 2023-06-30 total 1200.00")
    assert tdes_decrypt_ref(KEY24, blob) == b"settlement 2023-06-30 total 1200.00"


@case("tdea_encryption_disallowed", kind="policy", states=["s1", "s2", "s3"])
def t_refused(mod):
    f = need(mod, "build_partner_payload")
    try:
        blob = f(KEY24, b"settlement 2024")
    except PermissionError:
        return
    try:
        ok = tdes_decrypt_ref(KEY24, blob) == b"settlement 2024"
    except Exception:
        ok = False
    assert not ok, "three-key TDEA encryption performed after 2023"
