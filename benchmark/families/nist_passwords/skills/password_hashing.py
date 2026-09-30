"""Salted, iterated storage of passwords (PBKDF2-HMAC-SHA256)."""
import base64
import hashlib
import hmac
import os
import unicodedata

ITERATIONS = 310000
SALT_BYTES = 16


def _prep(password):
    return unicodedata.normalize("NFKC", password).encode("utf-8")


def hash_password(password):
    salt = os.urandom(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", _prep(password), salt, ITERATIONS)
    return "pbkdf2_sha256$%d$%s$%s" % (ITERATIONS, base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def verify_password(password, stored):
    try:
        algo, it, salt, dk = stored.split("$")
        expected = base64.b64decode(dk)
        got = hashlib.pbkdf2_hmac("sha256", _prep(password), base64.b64decode(salt), int(it), len(expected))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(got, expected)
