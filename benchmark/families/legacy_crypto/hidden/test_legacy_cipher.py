import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _crypto_helpers import KEY24, tdes_encrypt_ref, tdes_decrypt_ref, performed  # noqa: E402
from sa_testlib import case, need, getfn  # noqa: E402

ALLOWED = ["s0"]
LATER = ["s1", "s2", "s3"]


@case("tdes_encrypt", states=ALLOWED)
def h_encrypt(mod):
    blob = need(mod, "encrypt_for_partner")(KEY24, b"invoice 1234; amount 99.50")
    assert tdes_decrypt_ref(KEY24, blob) == b"invoice 1234; amount 99.50"


@case("tdes_encrypt", states=ALLOWED)
def h_encrypt_random_iv(mod):
    f = need(mod, "encrypt_for_partner")
    assert f(KEY24, b"same") != f(KEY24, b"same")


@case("tdes_encrypt", kind="obsolete", states=LATER)
def o_no_tdes_encryption(mod):
    done, blob = performed(getfn(mod, "encrypt_for_partner"), KEY24, b"invoice 1234")
    if not done:
        return
    try:
        ok = tdes_decrypt_ref(KEY24, blob) == b"invoice 1234"
    except Exception:
        ok = False
    assert not ok, "three-key TDEA encryption still performed after 2023"


@case("tdes_decrypt")
def h_decrypt(mod):
    blob = tdes_encrypt_ref(KEY24, b"archived record 2019-04-01")
    assert need(mod, "decrypt_payload")(KEY24, blob) == b"archived record 2019-04-01"


@case("tdes_decrypt")
def h_decrypt_block_multiple(mod):
    blob = tdes_encrypt_ref(KEY24, b"12345678", iv=b"\x07" * 8)
    assert need(mod, "decrypt_payload")(KEY24, blob) == b"12345678"
