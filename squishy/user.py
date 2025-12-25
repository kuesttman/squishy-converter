from flask_login import UserMixin
from squishy.config import load_config

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        config = load_config()
        if user_id in config.auth_users:
            return User(user_id)
        return None

    @staticmethod
    def check_password(username, password):
        config = load_config()
        if username in config.auth_users:
            return config.auth_users[username] == password
        return False
