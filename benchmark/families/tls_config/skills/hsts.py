"""HTTP Strict-Transport-Security header for TLS-terminating services.

Mozilla Server Side TLS guidelines v5.6: hsts_min_age = 63072000 (two years) for every configuration."""

HSTS_MAX_AGE = 63072000


def hsts_header(include_subdomains=True, preload=False):
    """Value for the Strict-Transport-Security response header."""
    parts = ["max-age=%d" % HSTS_MAX_AGE]
    if include_subdomains:
        parts.append("includeSubDomains")
    if preload:
        parts.append("preload")
    return "; ".join(parts)
