import bcrypt


def hash_for_partner_sync(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
