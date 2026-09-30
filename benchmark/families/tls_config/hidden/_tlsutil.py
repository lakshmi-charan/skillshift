"""Helpers for the tls_config hidden tests: fixture certificates, a thread-served local TLS server and
client contexts pinned to particular protocol versions.

Fixtures (generated once with the openssl CLI, OpenSSL 3.0.13, 100-year validity):
  openssl req -x509 -newkey rsa:2048 -nodes -days 36500 -sha256 -subj "/CN=localhost" \
      -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -addext "basicConstraints=critical,CA:TRUE" \
      -keyout localhost.key -out localhost.crt
  openssl req -x509 -newkey rsa:2048 -nodes -days 36500 -sha256 -subj "/CN=localhost" \
      -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -keyout untrusted.key -out untrusted.crt
"""
import contextlib
import os
import socket
import ssl
import threading
import warnings

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
CERT = os.path.join(FIX, "localhost.crt")
KEY = os.path.join(FIX, "localhost.key")
UNTRUSTED_CERT = os.path.join(FIX, "untrusted.crt")
UNTRUSTED_KEY = os.path.join(FIX, "untrusted.key")
PAYLOAD = b"hello from the test server\n"

V = {"TLSv1": ssl.TLSVersion.TLSv1, "TLSv1.1": ssl.TLSVersion.TLSv1_1,
     "TLSv1.2": ssl.TLSVersion.TLSv1_2, "TLSv1.3": ssl.TLSVersion.TLSv1_3}
RANK = {ssl.TLSVersion.MINIMUM_SUPPORTED: 0, ssl.TLSVersion.SSLv3: 0, ssl.TLSVersion.TLSv1: 1,
        ssl.TLSVersion.TLSv1_1: 2, ssl.TLSVersion.TLSv1_2: 3, ssl.TLSVersion.TLSv1_3: 4,
        ssl.TLSVersion.MAXIMUM_SUPPORTED: 4}


def plain_server_context(cert=CERT, key=KEY):
    """A server context with library defaults, used as the peer in client tests."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(cert, key)
    return ctx


def client_context(version=None, ciphers=None, cafile=CERT):
    """Verifying client context; `version` pins both min and max ('TLSv1' ... 'TLSv1.3')."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cafile)
        if version is not None:
            ctx.minimum_version = V[version]
            ctx.maximum_version = V[version]
            if version in ("TLSv1", "TLSv1.1"):
                ciphers = (ciphers or "DEFAULT") + ":@SECLEVEL=0"
        if ciphers:
            ctx.set_ciphers(ciphers)
    return ctx


@contextlib.contextmanager
def running_server(server_ctx, payload=PAYLOAD):
    """Serve one TLS connection on 127.0.0.1 in a thread. Yields (port, info); info gets 'version',
    'cipher' after a successful server-side handshake or 'error'."""
    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.bind(("127.0.0.1", 0))
    ls.listen(1)
    ls.settimeout(0.2)
    info = {}
    stop = threading.Event()

    def run():
        conn = None
        while not stop.is_set():
            try:
                conn, _ = ls.accept()
                break
            except socket.timeout:
                continue
            except OSError:
                return
        if conn is None:
            return
        conn.settimeout(5)
        try:
            s = server_ctx.wrap_socket(conn, server_side=True)
            info["version"], info["cipher"] = s.version(), s.cipher()[0]
            s.sendall(payload)
            s.close()
        except Exception as e:  # noqa
            info["error"] = repr(e)
            conn.close()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    try:
        yield ls.getsockname()[1], info
    finally:
        stop.set()
        t.join(5)
        ls.close()


def handshake(server_ctx, client_ctx, hostname="localhost"):
    """Full handshake + read. Returns (version, cipher, data); raises the client-side exception."""
    with running_server(server_ctx) as (port, info):
        with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
            with client_ctx.wrap_socket(raw, server_hostname=hostname) as s:
                return s.version(), s.cipher()[0], s.recv(len(PAYLOAD))


def handshake_ok(server_ctx, client_ctx, hostname="localhost"):
    try:
        v, c, data = handshake(server_ctx, client_ctx, hostname)
    except (ssl.SSLError, OSError):
        return None
    return (v, c) if data == PAYLOAD else None


def pre13_ciphers(ctx):
    """Names of cipher suites enabled on ctx for TLS 1.2 and below."""
    return {c["name"] for c in ctx.get_ciphers() if c.get("protocol") != "TLSv1.3"}


def make_server(fn, *args):
    """Call a server-context factory with DeprecationWarnings silenced."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fn(*args)


def accepts_below_tls12(ctx):
    """True if ctx is configured to allow, or actually negotiates, a protocol older than TLS 1.2."""
    no_old = (ctx.options & ssl.OP_NO_TLSv1) and (ctx.options & ssl.OP_NO_TLSv1_1)
    if RANK.get(ctx.minimum_version, 0) < 3 and not no_old:
        return True
    for v in ("TLSv1", "TLSv1.1"):
        if handshake_ok(ctx, client_context(v)):
            return True
    return False
