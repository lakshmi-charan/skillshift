def must_change_password(user, today):
    return bool(user["compromised"])
