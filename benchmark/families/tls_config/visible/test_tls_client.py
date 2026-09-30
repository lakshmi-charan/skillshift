import os
import socket
import ssl
import tempfile
import threading

from sa_testlib import case, need

# Test certificate for "localhost" (self-signed, RSA 2048, valid 100 years); generated with the openssl CLI.
TEST_CERT = """\
-----BEGIN CERTIFICATE-----
MIIDJzCCAg+gAwIBAgIUENaMPRzrPEVPZCCQbEPui7yuTzUwDQYJKoZIhvcNAQEL
BQAwFDESMBAGA1UEAwwJbG9jYWxob3N0MCAXDTI2MDkzMDAyNDgwNVoYDzIxMjYw
OTA2MDI0ODA1WjAUMRIwEAYDVQQDDAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQDdNwKisvK+XoGyhTOQY/xF31eErPGLMvlGUcIDSzA7
LOMSIqDZY4JLJ1ieAIvFHHuB0bJaLVYJVnKpFkTYtqz5zv4Z6YSVkkvTv2JzlIM8
a4DW0+ynjUr+X8OIy2UlCp/ohIdbf1lYimNg/GOe+5schNJ0H/zhkPEZnODjK4A4
tOPWPxs+e/kJBwwnLpE+wglCIL2yQoI/t568Ae+Ufck893qrLFwpsPUX8Euhmwm5
ytCTaFUaEGufafXaXiaJltRVDW3nWIRa2qJ7ya+DpodcYB+qK/0Sw9vy+scQdjot
qWNUnD5AQ7ZkjQgCfHh0WaDh/U5nXMI6GaSjClb4UdmXAgMBAAGjbzBtMB0GA1Ud
DgQWBBT2ovD7ZvpmBeKP9x6AKfzQ7a/QfzAfBgNVHSMEGDAWgBT2ovD7ZvpmBeKP
9x6AKfzQ7a/QfzAaBgNVHREEEzARgglsb2NhbGhvc3SHBH8AAAEwDwYDVR0TAQH/
BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAcbAa7Hda++PhLq9qZOh1GyqiBtCl
iArjza51A2LY/0Km+uwRhVCoZciXDIwOdRpnsc+wvBjlLykwGjqJ8fzt7EE/kigf
uet+OZ9CaYoh9IEDBpj46YZru5bq2B0Bdmi/M17+TWPlclrbeGe5Q+NEAiToC2yg
2Sh7z/u8mFhUNNtzhLqbP5DCQ1d5ezLnqzwSqrkB+gZRR50LDo8BUel/Fdcihshf
TpgLcMdNFcMOrDCKTjTX/9p2hafCHhjMbDf/zN9BPq37KhOAhDxGCqbnnWZEBmNq
uRpuKPeRN/7iR6V+UFJ+YgTbFurGtIUZ184H9JoZM9h0htD65r01Ev+kMg==
-----END CERTIFICATE-----
"""
TEST_KEY = """\
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDdNwKisvK+XoGy
hTOQY/xF31eErPGLMvlGUcIDSzA7LOMSIqDZY4JLJ1ieAIvFHHuB0bJaLVYJVnKp
FkTYtqz5zv4Z6YSVkkvTv2JzlIM8a4DW0+ynjUr+X8OIy2UlCp/ohIdbf1lYimNg
/GOe+5schNJ0H/zhkPEZnODjK4A4tOPWPxs+e/kJBwwnLpE+wglCIL2yQoI/t568
Ae+Ufck893qrLFwpsPUX8Euhmwm5ytCTaFUaEGufafXaXiaJltRVDW3nWIRa2qJ7
ya+DpodcYB+qK/0Sw9vy+scQdjotqWNUnD5AQ7ZkjQgCfHh0WaDh/U5nXMI6GaSj
Clb4UdmXAgMBAAECggEAJ1UDGnOP1opOLDQjzW4BqljCIlxvnAzlpnud7+D8A+GA
xDY0/EIFpiAqUPmO4G6mhRgISqFZ9VISE/9aIWAllEsaAfhzsvZulgkm058Z0HHa
2BeZMddc+KqFRTrI0pO3h+ucd4fGlogQkGt/uQJKe4EgPDZ9y4tuWtv6XlnbM/mc
50K7qaIC0imha39VIm/yYBp00TNNpbMLGhUu0NuR8rw3VVumYVzdAaldAgPd3X6A
7bdAlaTw8ToVff359Khm3BGYNZrwXNhTp75syCLih/7q2ZUAKBCtlI6LOV5p7+lO
K75YN/ptv2teChhjOVPoL4jPUpWqxiNXT52Lg3lZCQKBgQD9mVz3JlQGTdB8tVvf
m1Zx2WxQ69/oYUG/DKPXjN8H4cZLF3TYwQssaN8XkUL7TGcEOp44eOzlezjMauCj
7Nu3ZX3BmvxBiapl4l7/hvGPqgvGND2rDlVOhUpADw2KVRzt/bPVjmJuGqqUDEZj
cacwU1a7BdkScGGJLTNlz5KzDwKBgQDfTyi1dW9UBQKGD5HZEVfSroRE+UOSisY4
gU1a9YUOIg6HA555SqHBYOFnqXahLQWgpQUSS4iuSXlIdG8h3c7MHxqzfSmWx0l3
/gvjap3oJ+DsxwNGKc4/oRLVuWlnuUfbT1xosBB0/SzonB2lGp51RV8UOTvFwwQU
O7jtxoNQ+QKBgE4cYNAXVCYk7aSbz9KN7BBhIcXDAVJ4MmIAKK8JyuCIoCUc8naY
7zIckyqVKYZxwAFDdNx8EquUSqhb+xlCqWJRtmxdqnkdSAjdstkN3XWcsMe564y2
e3wV/grBGDCVirWbQTr0AklbmVLEfSHALfjqknpEkNnnF4PDEmO3jb3tAoGBAK3X
Rv60dD15RPSubEEK0k6uE0RKtEMBi7xzVJAJ8FIHSz3qIFWWNwR+8hqr/zEMBoR/
0sniSX48rpEsK1O3BAU99aBjQJwjeltSR1j8J/+SA/TwHOljJC++qhX9qEPaJklh
p7PL1JPugCZ5Wk6swUzT+2eYAqM65RMHRzi7wICpAoGAeGkyQcIYg5D+DTQ42SlJ
CSrQ7TRAWdZVtIq7D/fMcWvu4g0WBhsU+xjt4h/P9C8Hxvp3LMIMN9H1Jerq0Bdz
5DKoKk2h+uruzJWtoWd2q0bL2tRZuOfNe8PFvOCS7E2qhFWIRq+PlrnvitZvp/YL
pY+a9UgFG/Xj4oEqrVngkE8=
-----END PRIVATE KEY-----
"""


def _cert_files():
    d = tempfile.mkdtemp(prefix="tls_test_")
    paths = []
    for name, pem in (("localhost.crt", TEST_CERT), ("localhost.key", TEST_KEY)):
        p = os.path.join(d, name)
        with open(p, "w") as fh:
            fh.write(pem)
        paths.append(p)
    return paths


def _serve_once(server_ctx):
    """Accept one TLS connection on 127.0.0.1 in a thread and send b"hi". Returns (port, thread)."""
    ls = socket.socket()
    ls.bind(("127.0.0.1", 0))
    ls.listen(1)
    ls.settimeout(5)

    def run():
        try:
            conn, _ = ls.accept()
            with server_ctx.wrap_socket(conn, server_side=True) as s:
                s.sendall(b"hi")
        except Exception:
            pass
        finally:
            ls.close()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return ls.getsockname()[1], t


def _server():
    cert, key = _cert_files()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(cert, key)
    return ctx, cert


@case("context_settings")
def test_client_context_verifies(mod):
    ctx = need(mod, "make_client_context")()
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname


@case("wrap_handshake")
def test_wrap_client_socket(mod):
    server, cert = _server()
    port, t = _serve_once(server)
    sock = socket.create_connection(("127.0.0.1", port), timeout=5)
    tls = need(mod, "wrap_client_socket")(sock, "localhost", cert)
    assert tls.recv(2) == b"hi"
    tls.close()
    t.join(5)


@case("wrap_hostname_check")
def test_wrong_hostname_rejected(mod):
    server, cert = _server()
    port, t = _serve_once(server)
    sock = socket.create_connection(("127.0.0.1", port), timeout=5)
    try:
        need(mod, "wrap_client_socket")(sock, "www.example.com", cert)
    except ssl.CertificateError:
        return
    finally:
        sock.close()
        t.join(5)
    raise AssertionError("host name mismatch not detected")
