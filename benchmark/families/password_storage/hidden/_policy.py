"""Machine-readable encoding of the OWASP Password Storage Cheat Sheet revisions used by the hidden tests.
Each value is transcribed from the verbatim revision text in ../docs (commit given per state)."""
POLICY = {
    # s0 = 728bbcd (2021-03-17)
    "s0": dict(primary="bcrypt", sha256=310000, sha512=120000, sha1=720000, sha1_new=True,
               argon2_m=None, scrypt_ln=None, bcrypt_new=True, bcrypt_wf=12, bcrypt_limit=("chars", 64)),
    # s1 = 422ec84 (2022-06-10)
    "s1": dict(primary="argon2id", sha256=310000, sha512=120000, sha1=720000, sha1_new=True,
               argon2_m=15 * 1024, scrypt_ln=16, bcrypt_new=True, bcrypt_wf=10, bcrypt_limit=("bytes", 72)),
    # s2 = f14bc4c (2023-01-24), includes ba94e5c (2023-01-23)
    "s2": dict(primary="argon2id", sha256=600000, sha512=210000, sha1=1300000, sha1_new=True,
               argon2_m=19 * 1024, scrypt_ln=17, bcrypt_new=True, bcrypt_wf=10, bcrypt_limit=("bytes", 72)),
    # s3 = f387056 (2024-12-09): bcrypt only for legacy systems where Argon2 and scrypt are unavailable
    "s3": dict(primary="argon2id", sha256=600000, sha512=210000, sha1=1300000, sha1_new=True,
               argon2_m=19 * 1024, scrypt_ln=17, bcrypt_new=False, bcrypt_wf=10, bcrypt_limit=("bytes", 72)),
    # s4 = 02bfdad (2026-03-26)
    "s4": dict(primary="argon2id", sha256=600000, sha512=220000, sha1=1400000, sha1_new=True,
               argon2_m=19 * 1024, scrypt_ln=17, bcrypt_new=False, bcrypt_wf=10, bcrypt_limit=("bytes", 72)),
    # s5 = c3c1952 (2026-05-12): PBKDF2-HMAC-SHA1 legacy only
    "s5": dict(primary="argon2id", sha256=600000, sha512=220000, sha1=1400000, sha1_new=False,
               argon2_m=19 * 1024, scrypt_ln=17, bcrypt_new=False, bcrypt_wf=10, bcrypt_limit=("bytes", 72)),
}
ALL = list(POLICY)


def states(pred):
    return [s for s, p in POLICY.items() if pred(p)]


def refused(fn, *args):
    """True if calling fn is refused (raises) or fn is absent."""
    if fn is None:
        return True
    try:
        fn(*args)
    except Exception:
        return True
    return False
