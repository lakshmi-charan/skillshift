"""Server-side TLS context for the Mozilla "modern" configuration (TLS 1.3 only).

Values from the Mozilla Server Side TLS guidelines v5.6
(https://ssl-config.mozilla.org/guidelines/5.6.json, configurations.modern):
TLS 1.3 only (OpenSSL's default TLS 1.3 suites), server_preferred_order = false."""
import ssl


def make_modern_server_context(certfile, keyfile=None):
    """Return an SSLContext for services whose clients all support TLS 1.3 (Mozilla "modern")."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.options &= ~ssl.OP_CIPHER_SERVER_PREFERENCE
    ctx.load_cert_chain(certfile, keyfile)
    return ctx
