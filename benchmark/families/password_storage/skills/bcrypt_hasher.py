"""bcrypt password hashing (OWASP 2021: work factor 12 or more, password limit of 64 characters)."""
import bcrypt

ROUNDS = 12
MAX_CHARS = 64


def hash_bcrypt(password):
    """Hash a new password with bcrypt; passwords over the length limit are rejected."""
    if len(password) > MAX_CHARS:
        raise ValueError("password longer than %d characters" % MAX_CHARS)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(ROUNDS)).decode("ascii")


def verify_bcrypt(password, encoded):
    """Check a password against a stored $2a$/$2b$/$2y$ bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), encoded.encode("ascii"))
    except ValueError:
        return False
