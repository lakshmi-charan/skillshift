"""Password change policy (SP 800-63B-4: no periodic changes; force a change on evidence of compromise)."""


def password_change_required(last_changed, today, compromised=False):
    return bool(compromised)
