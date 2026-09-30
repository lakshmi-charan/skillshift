import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _crypto_helpers import KEY24, tdes_encrypt_ref  # noqa: E402
from sa_testlib import case, need  # noqa: E402


@case("functional")
def t_read(mod):
    blob = tdes_encrypt_ref(KEY24, b"archived settlement 2019", iv=b"\x05" * 8)
    assert need(mod, "read_archived_payload")(KEY24, blob) == b"archived settlement 2019"
