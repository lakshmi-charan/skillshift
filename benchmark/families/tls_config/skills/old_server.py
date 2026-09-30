"""Server-side TLS context for the Mozilla "old" configuration, for services that must accept
legacy clients (Windows XP IE8, Android 2.3, Java 6, ...).

Values from the Mozilla Server Side TLS guidelines v5.6
(https://ssl-config.mozilla.org/guidelines/5.6.json, configurations.old):
TLS 1.0 - TLS 1.3, the OpenSSL cipher list below, server_preferred_order = true."""
import ssl

OLD_CIPHERS = ":".join([
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "DHE-RSA-AES128-GCM-SHA256",
    "DHE-RSA-AES256-GCM-SHA384",
    "DHE-RSA-CHACHA20-POLY1305",
    "ECDHE-ECDSA-AES128-SHA256",
    "ECDHE-RSA-AES128-SHA256",
    "ECDHE-ECDSA-AES128-SHA",
    "ECDHE-RSA-AES128-SHA",
    "ECDHE-ECDSA-AES256-SHA384",
    "ECDHE-RSA-AES256-SHA384",
    "ECDHE-ECDSA-AES256-SHA",
    "ECDHE-RSA-AES256-SHA",
    "DHE-RSA-AES128-SHA256",
    "DHE-RSA-AES256-SHA256",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384",
    "AES128-SHA256",
    "AES256-SHA256",
    "AES128-SHA",
    "AES256-SHA",
    "DES-CBC3-SHA",
])


def make_old_server_context(certfile, keyfile=None):
    """Return an SSLContext that legacy TLS 1.0/1.1 clients can connect to (Mozilla "old")."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1
    # Builds with a raised default security level (Debian/Ubuntu openssl.cnf, OpenSSL 3) refuse
    # TLS 1.0/1.1 and SHA-1 handshakes unless the level is lowered explicitly.
    ctx.set_ciphers(OLD_CIPHERS + ":@SECLEVEL=0")
    # server_preferred_order is true for old: the server's order protects legacy clients
    ctx.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
    ctx.load_cert_chain(certfile, keyfile)
    return ctx
