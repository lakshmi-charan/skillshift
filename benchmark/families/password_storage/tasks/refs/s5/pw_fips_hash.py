import base64
import hashlib
import hmac
import os

IT = {"sha1": 1400000, "sha256": 600000, "sha512": 220000}


def fips_password_hash(password, digest):
    if digest == "sha1":
        raise PermissionError("PBKDF2-HMAC-SHA1 is legacy only")
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac(digest, password.encode(), salt, IT[digest])
    return "$pbkdf2-%s$%d$%s$%s" % (digest, IT[digest], base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def fips_verify(password, stored):
    _, scheme, it, salt, dk = stored.split("$")
    exp = base64.b64decode(dk)
    got = hashlib.pbkdf2_hmac(scheme.split("-", 1)[1], password.encode(), base64.b64decode(salt), int(it), len(exp))
    return hmac.compare_digest(got, exp)
