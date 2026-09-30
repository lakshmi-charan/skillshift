"""bcrypt password hashing (OWASP 2021: work factor 12 or more, password limit of 64 characters)."""
import bcrypt

ROUNDS = 12
MAX_BYTES = 72


def hash_bcrypt(password):
    """Hash a new password with bcrypt; passwords over the length limit are rejected."""
    data = password.encode("utf-8")
    if len(data) > MAX_BYTES:
        raise ValueError("password longer than %d bytes" % MAX_BYTES)
    return bcrypt.hashpw(data, bcrypt.gensalt(ROUNDS)).decode("ascii")


def verify_bcrypt(password, encoded):
    """Check a password against a stored $2a$/$2b$/$2y$ bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), encoded.encode("ascii"))
    except ValueError:
        return False
