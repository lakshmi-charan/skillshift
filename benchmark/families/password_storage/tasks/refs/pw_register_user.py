import bcrypt


def register_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def check_login(password, stored):
    return bcrypt.checkpw(password.encode(), stored.encode())
