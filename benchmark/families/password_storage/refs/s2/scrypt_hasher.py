"""scrypt password hashing via hashlib."""
import base64
import hashlib
import hmac
import os

LOG2_N, R, P = 17, 8, 1          # N = 2^17, r = 8, p = 1
MAXMEM = 2 ** 27 + 2 ** 22       # OpenSSL memory ceiling for these parameters
DKLEN = 32


def _b64(b):
    return base64.b64encode(b).decode("ascii").rstrip("=")


def _unb64(s):
    return base64.b64decode(s + "=" * (-len(s) % 4))


def hash_scrypt(password):
    """Return $scrypt$ln=<log2 N>,r=<r>,p=<p>$<salt_b64>$<hash_b64>."""
    salt = os.urandom(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2 ** LOG2_N, r=R, p=P, maxmem=MAXMEM, dklen=DKLEN)
    return "$scrypt$ln=%d,r=%d,p=%d$%s$%s" % (LOG2_N, R, P, _b64(salt), _b64(dk))


def verify_scrypt(password, encoded):
    """Check a password against a stored $scrypt$ hash with any parameters."""
    try:
        _, _, params, salt, dk = encoded.split("$")
        kv = dict(item.split("=") for item in params.split(","))
        ln, r, p = int(kv["ln"]), int(kv["r"]), int(kv["p"])
        expected = _unb64(dk)
        got = hashlib.scrypt(password.encode("utf-8"), salt=_unb64(salt), n=2 ** ln, r=r, p=p,
                             maxmem=256 * r * (2 ** ln) + 2 ** 22, dklen=len(expected))
    except (ValueError, KeyError, IndexError):
        return False
    return hmac.compare_digest(got, expected)
