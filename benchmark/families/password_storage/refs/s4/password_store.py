"""Application-facing password storage API."""
import argon2_hasher as _argon2
import bcrypt_hasher as _bcrypt
import pbkdf2_hasher as _pbkdf2
import scrypt_hasher as _scrypt

# Minimum parameters for stored hashes; anything weaker is re-hashed at next login.
MIN_BCRYPT_ROUNDS = 10
MIN_PBKDF2 = {"sha1": 1400000, "sha256": 600000, "sha512": 220000}
MIN_ARGON2_MEMORY_KIB = 19456
MIN_ARGON2_TIME = 2
MIN_SCRYPT_LOG2_N = 17


def hash_new_password(password):
    """Hash a new password with the first-choice algorithm (Argon2id)."""
    return _argon2.hash_argon2(password)


def verify_password(password, encoded):
    """Verify against any supported stored format."""
    if encoded.startswith("$pbkdf2-"):
        return _pbkdf2.verify_pbkdf2(password, encoded)
    if encoded.startswith("$argon2"):
        return _argon2.verify_argon2(password, encoded)
    if encoded.startswith("$scrypt$"):
        return _scrypt.verify_scrypt(password, encoded)
    if encoded.startswith(("$2a$", "$2b$", "$2y$")):
        return _bcrypt.verify_bcrypt(password, encoded)
    return False


def needs_rehash(encoded):
    """True if the stored hash is weaker than the current minimum parameters."""
    if encoded.startswith(("$2a$", "$2b$", "$2y$")):
        return True  # bcrypt is legacy-only: re-hash with Argon2id at next login
    if encoded.startswith("$pbkdf2-"):
        _, scheme, iterations, _, _ = encoded.split("$")
        digest = scheme.split("-", 1)[1]
        return int(iterations) < MIN_PBKDF2.get(digest, float("inf"))
    if encoded.startswith("$argon2"):
        params = dict(kv.split("=") for kv in encoded.split("$")[3].split(","))
        return int(params["m"]) < MIN_ARGON2_MEMORY_KIB or int(params["t"]) < MIN_ARGON2_TIME
    if encoded.startswith("$scrypt$"):
        params = dict(kv.split("=") for kv in encoded.split("$")[2].split(","))
        return int(params["ln"]) < MIN_SCRYPT_LOG2_N
    return True
