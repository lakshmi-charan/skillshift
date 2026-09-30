"""New-password checks (NIST SP 800-63B-4 3.1.1.2)."""

MIN_LENGTH = 15         # single-factor passwords: minimum of 15 characters
MAX_LENGTH = 256


def check_new_password(password, username="", blocklist=()):
    reasons = []
    if len(password) < MIN_LENGTH:
        reasons.append("too_short")
    if len(password) > MAX_LENGTH:
        reasons.append("too_long")
    if password in set(blocklist):
        reasons.append("blocklisted")
    # the entire password is compared, not substrings (context-specific word = the username itself)
    if username and password.lower() == username.lower():
        reasons.append("contains_username")
    return reasons
