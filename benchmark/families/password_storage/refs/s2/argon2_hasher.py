"""Argon2id password hashing with argon2-cffi."""
import argon2

_HASHER = argon2.PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)  # 19 MiB, t=2, p=1


def hash_argon2(password):
    """Return an Argon2id PHC string, e.g. $argon2id$v=19$m=15360,t=2,p=1$..."""
    return _HASHER.hash(password)


def verify_argon2(password, encoded):
    """Check a password against a stored Argon2 hash with any parameters."""
    try:
        return argon2.PasswordHasher().verify(encoded, password)
    except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash, ValueError):
        return False
