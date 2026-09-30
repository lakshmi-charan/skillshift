"""Server-side TLS context for the Mozilla "intermediate" configuration.

Values from the Mozilla Server Side TLS guidelines v6.0
(https://ssl-config.mozilla.org/guidelines/6.0.json, configurations.intermediate):
TLS 1.2 + TLS 1.3, the OpenSSL cipher list below (ECDHE only; DHE suites removed in 5.8/6.0),
server_preferred_order = false."""
import ssl

INTERMEDIATE_CIPHERS = ":".join([
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-CHACHA20-POLY1305",
])


def make_intermediate_server_context(certfile, keyfile=None):
    """Return an SSLContext for a general-purpose TLS server (Mozilla "intermediate")."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers(INTERMEDIATE_CIPHERS)
    # server_preferred_order is false for intermediate: let the client pick its fastest cipher
    ctx.options &= ~ssl.OP_CIPHER_SERVER_PREFERENCE
    ctx.load_cert_chain(certfile, keyfile)
    return ctx
