import os
import ssl
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import profile, states  # noqa: E402
from _tlsutil import (CERT, KEY, client_context, handshake_ok, pre13_ciphers, make_server,  # noqa: E402
                      accepts_below_tls12)
from sa_testlib import case, need, getfn, STATE  # noqa: E402

P = profile(STATE, "old")
LIVE = states(lambda ps: "old" in ps)
GONE = states(lambda ps: "old" not in ps)


def _ctx(mod):
    return make_server(need(mod, "make_old_server_context"), CERT, KEY)


@case("legacy_clients", states=LIVE)
def h_tls10_client(mod):
    r = handshake_ok(_ctx(mod), client_context("TLSv1"))
    assert r is not None and r[0] == "TLSv1", "TLS 1.0 client could not connect"


@case("legacy_clients", states=LIVE)
def h_every_profile_version(mod):
    ctx = _ctx(mod)
    for v in P["tls_versions"]:
        r = handshake_ok(ctx, client_context(v))
        assert r is not None and r[0] == v, "%s client could not connect" % v


@case("legacy_clients", states=LIVE)
def h_tls10_rsa_kx(mod):
    # the oldest clients of the profile (e.g. IE8 on Windows XP) only offer plain-RSA CBC suites
    r = handshake_ok(_ctx(mod), client_context("TLSv1", "AES128-SHA:AES256-SHA"))
    assert r is not None and r[1] in ("AES128-SHA", "AES256-SHA"), r


@case("cipher_allowlist", kind="policy", states=LIVE)
def h_enabled_subset(mod):
    extra = sorted(pre13_ciphers(_ctx(mod)) - set(P["openssl"]))
    assert not extra, "cipher suites outside the old profile enabled: %s" % extra


@case("cipher_allowlist", kind="policy", states=LIVE)
def h_non_profile_refused(mod):
    r = handshake_ok(_ctx(mod), client_context("TLSv1.2", "DHE-RSA-AES128-SHA:CAMELLIA128-SHA:ECDHE-RSA-CAMELLIA128-SHA256"))
    assert r is None, "non-profile suite negotiated: %r" % (r,)


@case("server_cipher_order", states=LIVE)
def h_server_preference(mod):
    ctx = _ctx(mod)
    assert bool(ctx.options & ssl.OP_CIPHER_SERVER_PREFERENCE) == P["server_preferred_order"]


@case("server_cipher_order", states=LIVE)
def h_server_order_wins(mod):
    r = handshake_ok(_ctx(mod), client_context("TLSv1.2", "AES128-SHA:ECDHE-RSA-AES128-GCM-SHA256"))
    assert r is not None and r[1] == "ECDHE-RSA-AES128-GCM-SHA256", "server order not applied: %r" % (r,)


@case("profile_withdrawn", kind="obsolete", states=GONE)
def o_no_legacy_context(mod):
    f = getfn(mod, "make_old_server_context")
    if f is None:
        return
    try:
        ctx = make_server(f, CERT, KEY)
    except Exception:
        return
    assert not accepts_below_tls12(ctx), "context accepting TLS < 1.2 created although the Old profile is withdrawn"
