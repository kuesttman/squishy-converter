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
            stored = config.auth_users[username]
            try:
                from werkzeug.security import check_password_hash
                if check_password_hash(stored, password):
                    return True
            except (ValueError, TypeError):
                # Fallback to plain text if not a valid hash
                pass
            
            # Plain text check
            return stored == password
        return False
