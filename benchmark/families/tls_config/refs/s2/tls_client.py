"""TLS client helpers: contexts and sockets that verify the server certificate and host name."""
import ssl


def make_client_context(cafile=None):
    """Client SSLContext verifying the server chain (against `cafile` or the system store) and host name."""
    return ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)


def wrap_client_socket(sock, server_hostname, cafile=None):
    """Wrap a connected TCP socket in TLS; raise ssl.SSLError / ssl.CertificateError if the server's
    certificate is not trusted or does not match `server_hostname`.

    ssl.wrap_socket() and ssl.match_hostname() were removed in Python 3.12: the context performs chain
    and host-name verification during the handshake (and sends SNI)."""
    ctx = make_client_context(cafile)
    return ctx.wrap_socket(sock, server_hostname=server_hostname)
