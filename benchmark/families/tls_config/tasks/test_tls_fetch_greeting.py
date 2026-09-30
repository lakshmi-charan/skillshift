import os
import ssl
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _tlsutil import CERT, UNTRUSTED_CERT, UNTRUSTED_KEY, PAYLOAD, plain_server_context, running_server  # noqa: E402
from sa_testlib import case, need  # noqa: E402


def _fetch(mod, server_ctx, host="127.0.0.1", server_hostname="localhost"):
    f = need(mod, "fetch_greeting")
    with running_server(server_ctx) as (port, info):
        if server_hostname is None:
            return f(host, port, CERT)
        return f(host, port, CERT, server_hostname)


def _expect_tls_error(fn, what):
    try:
        fn()
    except (ssl.SSLError, ssl.CertificateError):
        return
    except Exception as e:  # noqa
        raise AssertionError("%s: expected ssl.SSLError/CertificateError, got %r" % (what, e))
    raise AssertionError("%s: connection accepted" % what)


@case("functional")
def t_greeting(mod):
    assert _fetch(mod, plain_server_context()) == PAYLOAD


@case("functional")
def t_default_hostname(mod):
    assert _fetch(mod, plain_server_context(), host="localhost", server_hostname=None) == PAYLOAD


@case("hostname_verification", kind="policy")
def t_wrong_host(mod):
    _expect_tls_error(lambda: _fetch(mod, plain_server_context(), server_hostname="wrong.example"), "wrong host")


@case("chain_verification", kind="policy")
def t_untrusted(mod):
    _expect_tls_error(lambda: _fetch(mod, plain_server_context(UNTRUSTED_CERT, UNTRUSTED_KEY)), "untrusted cert")
