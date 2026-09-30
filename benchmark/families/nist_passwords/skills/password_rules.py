"""New-password checks (NIST SP 800-63B 5.1.1.2 plus organisation rules)."""

MIN_LENGTH = 8          # SP 800-63B: at least 8 characters for subscriber-chosen secrets
MAX_LENGTH = 256        # we permit at least 64 characters


def check_new_password(password, username="", blocklist=()):
    """Return a list of rejection reasons; an empty list means the password is accepted."""
    reasons = []
    if len(password) < MIN_LENGTH:
        reasons.append("too_short")
    if len(password) > MAX_LENGTH:
        reasons.append("too_long")
    if password in set(blocklist):
        reasons.append("blocklisted")
    if username and username.lower() in password.lower():
        reasons.append("contains_username")
    has_letter = any(ch.isalpha() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    if not (has_letter and has_digit):
        reasons.append("needs_letter_and_digit")
    return reasons
