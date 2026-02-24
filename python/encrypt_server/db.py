import pickle
import os
import traceback

class Database:
    def __init__(self):
        if os.path.exists('users.pk1'):
            try:
                with open('users.pk1', 'rb') as f:
                    self.users = pickle.load(f)
            except Exception:
                print(traceback.format_exc())
                self.users = {}

        else:
            self.users = {}

    def add_user_to_db(self, user):
        self.users[user.username] = user

        with open('users.pk1', 'wb') as f:
            pickle.dump(self.users, f)
