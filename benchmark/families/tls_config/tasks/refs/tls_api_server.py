import ssl

# Mozilla intermediate profile, ECDHE AEAD suites only
CIPHERS = ("ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:"
           "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305")


def make_api_server_context(certfile, keyfile):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers(CIPHERS)
    ctx.options &= ~ssl.OP_CIPHER_SERVER_PREFERENCE
    ctx.load_cert_chain(certfile, keyfile)
    return ctx
