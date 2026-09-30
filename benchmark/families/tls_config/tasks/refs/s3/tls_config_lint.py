import ssl

# Mozilla Server Side TLS guidelines 6.0: profile -> (lowest TLS version, TLS<=1.2 suites or None)
INTERMEDIATE = ['ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES256-GCM-SHA384', 'ECDHE-RSA-AES256-GCM-SHA384', 'ECDHE-ECDSA-CHACHA20-POLY1305', 'ECDHE-RSA-CHACHA20-POLY1305']
PROFILES = {
    "modern": (ssl.TLSVersion.TLSv1_3, None),
    "intermediate": (ssl.TLSVersion.TLSv1_2, set(INTERMEDIATE)),
}


def server_context_compliant(ctx):
    if ctx.maximum_version not in (ssl.TLSVersion.MAXIMUM_SUPPORTED, ssl.TLSVersion.TLSv1_3):
        return False
    legacy = {c["name"] for c in ctx.get_ciphers() if c["protocol"] != "TLSv1.3"}
    for lowest, allowed in PROFILES.values():
        if ctx.minimum_version == lowest and (allowed is None or legacy <= allowed):
            return True
    return False
