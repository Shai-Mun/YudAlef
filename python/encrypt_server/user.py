import hashlib
import string
import secrets


class User:
    def __init__(self, username, fname, lname, email, phone):
        self.username = username
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone = phone
        self.hashpass = ""
        self.salt = ""

    def __str__(self):
        return super().__str__()

    @staticmethod
    def hash_salt_passwd(passwd, salt=None):
        if not salt:
            salt = User.salt_generator()
        both = salt + passwd
        return salt, User.hash_item(both)

    @staticmethod
    def hash_item(item):
        """
        return hashed 256 string
        """
        m = hashlib.sha256()
        m.update(item.encode())
        return m.hexdigest()

    @staticmethod
    def salt_generator(length=16):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        salt = ''.join(secrets.choice(alphabet) for _ in range(length))
        return salt