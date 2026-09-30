import os
import ssl
import sys
import warnings

sys.path.insert(0, os.path.dirname(__file__))
from _policy import profiles, min_version, states  # noqa: E402
from _tlsutil import V, pre13_ciphers  # noqa: E402
from sa_testlib import case, need, getfn, STATE  # noqa: E402

PROFILES = profiles(STATE)
LIVE = states(lambda ps: "old" in ps)
GONE = states(lambda ps: "old" not in ps)

ECDHE = ["ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-RSA-AES128-GCM-SHA256", "ECDHE-ECDSA-AES256-GCM-SHA384",
         "ECDHE-RSA-AES256-GCM-SHA384", "ECDHE-ECDSA-CHACHA20-POLY1305", "ECDHE-RSA-CHACHA20-POLY1305"]
DHE_GCM = ["DHE-RSA-AES128-GCM-SHA256", "DHE-RSA-AES256-GCM-SHA384"]
LEGACY = ["ECDHE-RSA-AES128-SHA256", "ECDHE-RSA-AES128-SHA", "ECDHE-RSA-AES256-SHA", "AES128-GCM-SHA256",
          "AES128-SHA", "AES256-SHA"]


def _ctx(minv, ciphers, maxv=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        c.minimum_version = V[minv]
        if maxv:
            c.maximum_version = V[maxv]
        c.set_ciphers(":".join(ciphers))
    return c


def _expected(ctx):
    """Profile of the guidelines in force that the context matches (requirement of matching_profile)."""
    if ctx.maximum_version not in (ssl.TLSVersion.MAXIMUM_SUPPORTED, ssl.TLSVersion.TLSv1_3):
        return None
    for name, p in PROFILES.items():
        if V[min_version(p)] != ctx.minimum_version:
            continue
        if min_version(p) == "TLSv1.3" or pre13_ciphers(ctx) <= set(p["openssl"]):
            return name
    return None


def _check(mod, ctx):
    got = need(mod, "matching_profile")(ctx)
    exp = _expected(ctx)
    assert got == exp, "matching_profile returned %r, expected %r" % (got, exp)


@case("modern")
def h_modern(mod):
    _check(mod, _ctx("TLSv1.3", ECDHE))
    _check(mod, _ctx("TLSv1.3", ECDHE, maxv="TLSv1.3"))
    assert need(mod, "matching_profile")(_ctx("TLSv1.3", ECDHE)) == "modern"


@case("intermediate_ecdhe")
def h_intermediate_full(mod):
    assert need(mod, "matching_profile")(_ctx("TLSv1.2", ECDHE)) == "intermediate"


@case("intermediate_ecdhe")
def h_intermediate_subset(mod):
    f = need(mod, "matching_profile")
    assert f(_ctx("TLSv1.2", ["ECDHE-RSA-AES128-GCM-SHA256"])) == "intermediate"
    assert f(_ctx("TLSv1.2", ["ECDHE-ECDSA-CHACHA20-POLY1305", "ECDHE-RSA-AES256-GCM-SHA384"])) == "intermediate"


@case("intermediate_dhe")
def h_dhe_gcm(mod):
    _check(mod, _ctx("TLSv1.2", ECDHE + DHE_GCM))
    _check(mod, _ctx("TLSv1.2", ["ECDHE-RSA-AES128-GCM-SHA256", "DHE-RSA-AES256-GCM-SHA384"]))


@case("intermediate_dhe")
def h_dhe_chacha(mod):
    _check(mod, _ctx("TLSv1.2", ECDHE + ["DHE-RSA-CHACHA20-POLY1305"]))
    _check(mod, _ctx("TLSv1.2", ECDHE + DHE_GCM + ["DHE-RSA-CHACHA20-POLY1305"]))


@case("old_profile", states=LIVE)
def h_old(mod):
    f = need(mod, "matching_profile")
    assert f(_ctx("TLSv1", ECDHE + DHE_GCM + LEGACY)) == "old"
    assert f(_ctx("TLSv1", ["AES128-SHA", "ECDHE-RSA-AES128-GCM-SHA256"])) == "old"


@case("old_profile", states=LIVE)
def h_old_foreign_cipher(mod):
    assert need(mod, "matching_profile")(_ctx("TLSv1", ECDHE + ["DHE-RSA-AES128-SHA"])) is None


@case("old_profile", kind="obsolete", states=GONE)
def o_old_withdrawn(mod):
    f = getfn(mod, "matching_profile")
    if f is None:
        return
    for ciphers in (ECDHE + DHE_GCM + LEGACY, ["AES128-SHA", "ECDHE-RSA-AES128-GCM-SHA256"]):
        try:
            got = f(_ctx("TLSv1", ciphers))
        except Exception:
            continue
        assert got is None, "TLS 1.0 context classified as %r although the Old profile is withdrawn" % got


@case("reject_other")
def h_cbc_at_tls12(mod):
    f = need(mod, "matching_profile")
    assert f(_ctx("TLSv1.2", ECDHE + ["ECDHE-RSA-AES128-SHA256"])) is None
    assert f(_ctx("TLSv1.2", ["AES128-GCM-SHA256"])) is None


@case("reject_other")
def h_odd_versions(mod):
    f = need(mod, "matching_profile")
    assert f(_ctx("TLSv1.1", ECDHE)) is None
    assert f(_ctx("TLSv1.2", ECDHE, maxv="TLSv1.2")) is None
