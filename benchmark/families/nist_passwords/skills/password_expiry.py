"""Password change policy."""
import datetime

MAX_AGE_DAYS = 365


def password_change_required(last_changed, today, compromised=False):
    """True when the user must change the password now."""
    if compromised:
        return True
    if isinstance(last_changed, datetime.datetime):
        last_changed = last_changed.date()
    if isinstance(today, datetime.datetime):
        today = today.date()
    return (today - last_changed).days >= MAX_AGE_DAYS
