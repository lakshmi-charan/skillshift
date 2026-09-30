"""TLS client helpers: contexts and sockets that verify the server certificate and host name."""
import ssl


def make_client_context(cafile=None):
    """Client SSLContext verifying the server chain (against `cafile` or the system store) and host name."""
    return ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)


def wrap_client_socket(sock, server_hostname, cafile=None):
    """Wrap a connected TCP socket in TLS; raise ssl.SSLError / ssl.CertificateError if the server's
    certificate is not trusted or does not match `server_hostname`."""
    tls = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_REQUIRED, ca_certs=cafile,
                          ssl_version=ssl.PROTOCOL_TLS)
    try:
        ssl.match_hostname(tls.getpeercert(), server_hostname)
    except ssl.CertificateError:
        tls.close()
        raise
    return tls
