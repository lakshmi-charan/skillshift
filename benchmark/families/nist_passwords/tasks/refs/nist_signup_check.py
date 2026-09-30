def validate_signup(username, password, breached):
    reasons = []
    if len(password) < 8:
        reasons.append("too_short")
    if password in breached:
        reasons.append("blocklisted")
    if username and username.lower() in password.lower():
        reasons.append("contains_username")
    if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
        reasons.append("needs_letter_and_digit")
    return reasons
