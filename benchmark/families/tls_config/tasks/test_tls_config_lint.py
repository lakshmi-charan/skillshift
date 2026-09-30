import os
import ssl
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _policy import profiles, min_version  # noqa: E402
from _tlsutil import V, pre13_ciphers  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

ECDHE = ["ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-RSA-AES128-GCM-SHA256", "ECDHE-ECDSA-AES256-GCM-SHA384",
         "ECDHE-RSA-AES256-GCM-SHA384", "ECDHE-ECDSA-CHACHA20-POLY1305", "ECDHE-RSA-CHACHA20-POLY1305"]
DHE_GCM = ["DHE-RSA-AES128-GCM-SHA256", "DHE-RSA-AES256-GCM-SHA384"]
LEGACY = ["ECDHE-RSA-AES128-SHA256", "ECDHE-RSA-AES128-SHA", "AES128-GCM-SHA256", "AES128-SHA", "AES256-SHA"]


def _ctx(minv, ciphers, maxv=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        c.minimum_version = V[minv]
        if maxv:
            c.maximum_version = V[maxv]
        c.set_ciphers(":".join(ciphers))
    return c


def _compliant(ctx):
    if ctx.maximum_version not in (ssl.TLSVersion.MAXIMUM_SUPPORTED, ssl.TLSVersion.TLSv1_3):
        return False
    for p in profiles(STATE).values():
        if V[min_version(p)] == ctx.minimum_version and (
                min_version(p) == "TLSv1.3" or pre13_ciphers(ctx) <= set(p["openssl"])):
            return True
    return False


def _check(mod, cases):
    f = need(mod, "server_context_compliant")
    wrong = [label for label, ctx in cases if bool(f(ctx)) != _compliant(ctx)]
    assert not wrong, "wrong verdict for: %s" % wrong


@case("stable_verdicts")
def t_stable(mod):
    _check(mod, [("tls13-only", _ctx("TLSv1.3", ECDHE)), ("tls12-ecdhe", _ctx("TLSv1.2", ECDHE)),
                 ("tls12-one-ecdhe", _ctx("TLSv1.2", ECDHE[1:2])),
                 ("tls12-cbc", _ctx("TLSv1.2", ECDHE + ["ECDHE-RSA-AES128-SHA256"])),
                 ("tls11-min", _ctx("TLSv1.1", ECDHE)), ("tls12-max12", _ctx("TLSv1.2", ECDHE, "TLSv1.2"))])


@case("dhe_suites", kind="policy")
def t_dhe(mod):
    _check(mod, [("tls12-dhe-gcm", _ctx("TLSv1.2", ECDHE + DHE_GCM)),
                 ("tls12-dhe-chacha", _ctx("TLSv1.2", ECDHE + ["DHE-RSA-CHACHA20-POLY1305"]))])


@case("legacy_protocols", kind="policy")
def t_legacy(mod):
    _check(mod, [("tls10-old-suites", _ctx("TLSv1", ECDHE + DHE_GCM + LEGACY)),
                 ("tls10-foreign-suite", _ctx("TLSv1", ECDHE + ["DHE-RSA-AES128-SHA"]))])
