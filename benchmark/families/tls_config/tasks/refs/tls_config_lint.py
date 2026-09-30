import ssl

# Mozilla Server Side TLS guidelines 5.6: profile -> (lowest TLS version, TLS<=1.2 suites or None)
INTERMEDIATE = ['ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES256-GCM-SHA384', 'ECDHE-RSA-AES256-GCM-SHA384', 'ECDHE-ECDSA-CHACHA20-POLY1305', 'ECDHE-RSA-CHACHA20-POLY1305', 'DHE-RSA-AES128-GCM-SHA256', 'DHE-RSA-AES256-GCM-SHA384']
PROFILES = {
    "modern": (ssl.TLSVersion.TLSv1_3, None),
    "intermediate": (ssl.TLSVersion.TLSv1_2, set(INTERMEDIATE)),
    "old": (ssl.TLSVersion.TLSv1, set(['ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES256-GCM-SHA384', 'ECDHE-RSA-AES256-GCM-SHA384', 'ECDHE-ECDSA-CHACHA20-POLY1305', 'ECDHE-RSA-CHACHA20-POLY1305', 'DHE-RSA-AES128-GCM-SHA256', 'DHE-RSA-AES256-GCM-SHA384', 'DHE-RSA-CHACHA20-POLY1305', 'ECDHE-ECDSA-AES128-SHA256', 'ECDHE-RSA-AES128-SHA256', 'ECDHE-ECDSA-AES128-SHA', 'ECDHE-RSA-AES128-SHA', 'ECDHE-ECDSA-AES256-SHA384', 'ECDHE-RSA-AES256-SHA384', 'ECDHE-ECDSA-AES256-SHA', 'ECDHE-RSA-AES256-SHA', 'DHE-RSA-AES128-SHA256', 'DHE-RSA-AES256-SHA256', 'AES128-GCM-SHA256', 'AES256-GCM-SHA384', 'AES128-SHA256', 'AES256-SHA256', 'AES128-SHA', 'AES256-SHA', 'DES-CBC3-SHA'])),
}


def server_context_compliant(ctx):
    if ctx.maximum_version not in (ssl.TLSVersion.MAXIMUM_SUPPORTED, ssl.TLSVersion.TLSv1_3):
        return False
    legacy = {c["name"] for c in ctx.get_ciphers() if c["protocol"] != "TLSv1.3"}
    for lowest, allowed in PROFILES.values():
        if ctx.minimum_version == lowest and (allowed is None or legacy <= allowed):
            return True
    return False
