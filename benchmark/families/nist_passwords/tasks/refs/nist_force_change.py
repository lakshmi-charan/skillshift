def must_change_password(user, today):
    return bool(user["compromised"]) or (today - user["last_changed"]).days >= 365
