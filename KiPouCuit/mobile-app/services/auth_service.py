import json
import os

class AuthService:
    FILE = "token.json"

    def save_token(self, token, username=None):
        data = {
            "token": token,
            "username": username
        }
        with open(self.FILE, "w") as f:
            json.dump(data, f)

    def load_token(self):
        if not os.path.exists(self.FILE):
            return None
        try:
            with open(self.FILE, "r") as f:
                return json.load(f)
        except:
            return None

    def clear(self):
        if os.path.exists(self.FILE):
            os.remove(self.FILE)