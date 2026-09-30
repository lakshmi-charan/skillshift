def validate_signup(username, password, breached):
    reasons = []
    if len(password) < 15:
        reasons.append("too_short")
    if password in breached:
        reasons.append("blocklisted")
    if username and password.lower() == username.lower():
        reasons.append("contains_username")
    return reasons
