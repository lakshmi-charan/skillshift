"""PBKDF2-HMAC password hashing for the FIPS subsystem (OWASP Password Storage Cheat Sheet, 2021)."""
import base64
import hashlib
import hmac
import os

# OWASP: PBKDF2-HMAC-SHA1 720,000; PBKDF2-HMAC-SHA256 310,000; PBKDF2-HMAC-SHA512 120,000 iterations.
ITERATIONS = {"sha1": 1300000, "sha256": 600000, "sha512": 210000}
SALT_BYTES = 16


def _b64(b):
    return base64.b64encode(b).decode("ascii").rstrip("=")


def _unb64(s):
    return base64.b64decode(s + "=" * (-len(s) % 4))


def hash_pbkdf2(password, digest="sha256"):
    """Return $pbkdf2-<digest>$<iterations>$<salt_b64>$<hash_b64>."""
    if digest not in ITERATIONS:
        raise ValueError("unsupported digest: %s" % digest)
    iterations = ITERATIONS[digest]
    salt = os.urandom(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(digest, password.encode("utf-8"), salt, iterations)
    return "$pbkdf2-%s$%d$%s$%s" % (digest, iterations, _b64(salt), _b64(dk))


def verify_pbkdf2(password, encoded):
    """Check a password against any stored $pbkdf2-* hash (any digest, any iteration count)."""
    try:
        _, scheme, iterations, salt, dk = encoded.split("$")
        digest = scheme.split("-", 1)[1]
        expected = _unb64(dk)
        got = hashlib.pbkdf2_hmac(digest, password.encode("utf-8"), _unb64(salt), int(iterations), len(expected))
    except (ValueError, IndexError):
        return False
    return hmac.compare_digest(got, expected)
