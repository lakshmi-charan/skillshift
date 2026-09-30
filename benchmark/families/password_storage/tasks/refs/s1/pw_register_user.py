import argon2
import bcrypt

_PH = argon2.PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)


def register_password(password):
    return _PH.hash(password)


def check_login(password, stored):
    if stored.startswith("$argon2"):
        try:
            return argon2.PasswordHasher().verify(stored, password)
        except Exception:
            return False
    if stored.startswith(("$2a$", "$2b$", "$2y$")):
        return bcrypt.checkpw(password.encode(), stored.encode())
    return False
