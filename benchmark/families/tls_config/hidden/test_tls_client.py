import os
import socket
import ssl
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _tlsutil import (CERT, UNTRUSTED_CERT, UNTRUSTED_KEY, PAYLOAD, plain_server_context,  # noqa: E402
                      running_server, handshake, handshake_ok)
from sa_testlib import case, need  # noqa: E402

TLS_ERRORS = (ssl.SSLError, ssl.CertificateError)


def _wrap(mod, hostname, server_ctx):
    """Connect to a local server and call wrap_client_socket; returns (data, version) or raises."""
    f = need(mod, "wrap_client_socket")
    with running_server(server_ctx) as (port, info):
        sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        try:
            tls = f(sock, hostname, CERT)
            try:
                return tls.recv(len(PAYLOAD)), tls.version()
            finally:
                tls.close()
        finally:
            sock.close()


def _expect_tls_error(fn, what):
    try:
        fn()
    except TLS_ERRORS:
        return
    except Exception as e:  # noqa
        raise AssertionError("%s: expected ssl.SSLError/CertificateError, got %r" % (what, e))
    raise AssertionError("%s: connection was accepted" % what)


@case("context_settings", kind="policy")
def h_settings(mod):
    ctx = need(mod, "make_client_context")(CERT)
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname is True


@case("context_settings", kind="policy")
def h_settings_system_store(mod):
    ctx = need(mod, "make_client_context")()
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname is True


@case("context_handshake")
def h_ctx_ok(mod):
    ctx = need(mod, "make_client_context")(CERT)
    r = handshake_ok(plain_server_context(), ctx)
    assert r is not None and r[0] in ("TLSv1.2", "TLSv1.3"), r


@case("context_handshake")
def h_ctx_wrong_host(mod):
    ctx = need(mod, "make_client_context")(CERT)
    _expect_tls_error(lambda: handshake(plain_server_context(), ctx, "wrong.example"), "wrong host name")


@case("context_handshake")
def h_ctx_untrusted(mod):
    ctx = need(mod, "make_client_context")(CERT)
    _expect_tls_error(lambda: handshake(plain_server_context(UNTRUSTED_CERT, UNTRUSTED_KEY), ctx),
                      "untrusted certificate")


@case("wrap_handshake")
def h_wrap_ok(mod):
    data, version = _wrap(mod, "localhost", plain_server_context())
    assert data == PAYLOAD and version in ("TLSv1.2", "TLSv1.3"), (data, version)


@case("wrap_handshake")
def h_wrap_ok_ip(mod):
    data, _ = _wrap(mod, "127.0.0.1", plain_server_context())
    assert data == PAYLOAD


@case("wrap_hostname_check", kind="policy")
def h_wrap_wrong_host(mod):
    for host in ("wrong.example", "localhost.attacker.test"):
        _expect_tls_error(lambda: _wrap(mod, host, plain_server_context()), "wrong host name %s" % host)


@case("wrap_chain_check", kind="policy")
def h_wrap_untrusted(mod):
    _expect_tls_error(lambda: _wrap(mod, "localhost", plain_server_context(UNTRUSTED_CERT, UNTRUSTED_KEY)),
                      "untrusted certificate")
