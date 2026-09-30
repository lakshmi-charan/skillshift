"""Audit an ssl.SSLContext against the Mozilla Server Side TLS configurations.

Profile data from the Mozilla Server Side TLS guidelines v5.6
(https://ssl-config.mozilla.org/guidelines/5.6.json)."""
import ssl

_INTERMEDIATE = [
    "ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384", "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-CHACHA20-POLY1305", "ECDHE-RSA-CHACHA20-POLY1305",
    "DHE-RSA-AES128-GCM-SHA256", "DHE-RSA-AES256-GCM-SHA384",
]
_OLD = _INTERMEDIATE + [
    "DHE-RSA-CHACHA20-POLY1305",
    "ECDHE-ECDSA-AES128-SHA256", "ECDHE-RSA-AES128-SHA256", "ECDHE-ECDSA-AES128-SHA", "ECDHE-RSA-AES128-SHA",
    "ECDHE-ECDSA-AES256-SHA384", "ECDHE-RSA-AES256-SHA384", "ECDHE-ECDSA-AES256-SHA", "ECDHE-RSA-AES256-SHA",
    "DHE-RSA-AES128-SHA256", "DHE-RSA-AES256-SHA256",
    "AES128-GCM-SHA256", "AES256-GCM-SHA384", "AES128-SHA256", "AES256-SHA256", "AES128-SHA", "AES256-SHA",
    "DES-CBC3-SHA",
]

# profile -> (lowest TLS version, allowed TLS <= 1.2 cipher suites; None = TLS 1.2 and below unused)
PROFILES = {
    "modern": (ssl.TLSVersion.TLSv1_3, None),
    "intermediate": (ssl.TLSVersion.TLSv1_2, frozenset(_INTERMEDIATE)),
    "old": (ssl.TLSVersion.TLSv1, frozenset(_OLD)),
}


def enabled_legacy_ciphers(ctx):
    """Names of the TLS 1.2-and-below cipher suites enabled on ctx."""
    return {c["name"] for c in ctx.get_ciphers() if c["protocol"] != "TLSv1.3"}


def matching_profile(ctx):
    """Name of the Mozilla profile the server context matches, or None.

    A context matches a profile when its minimum_version is the profile's lowest TLS version, TLS 1.3 is
    not disabled, and every enabled TLS 1.2-and-below cipher suite is in the profile's cipher list."""
    if ctx.maximum_version not in (ssl.TLSVersion.MAXIMUM_SUPPORTED, ssl.TLSVersion.TLSv1_3):
        return None
    for name, (min_version, allowed) in PROFILES.items():
        if ctx.minimum_version != min_version:
            continue
        if allowed is None or enabled_legacy_ciphers(ctx) <= allowed:
            return name
    return None
