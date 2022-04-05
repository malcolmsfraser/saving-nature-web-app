from werkzeug.security import generate_password_hash

def get_users():
    users = {
    "admin": generate_password_hash("###")
    }
    return users