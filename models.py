from pony.orm import *
from passlib.hash import bcrypt_sha256
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime

db = Database()

class User(UserMixin, db.Entity):
    username = Optional(unicode, unique=True)
    password_hash = Optional(unicode)
    email = Required(unicode, unique=True)
    dt_registered = Optional(datetime, default=datetime.utcnow)
    dt_last_visit = Optional(datetime, default=datetime.utcnow)
    verified = Optional(bool, default=False)
    failed_login = Optional(int)
    last_failed_login = Optional(datetime, default=datetime.utcnow)
    ships = Set(lambda: Ship)

    def hash_password(self, password):
        self.password_hash = bcrypt_sha256.hash(password)

    def verify_password(self, password):
        return bcrypt_sha256.verify(password, self.password_hash)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

class Ship(db.Entity):
    user = Optional(lambda: User)
    yes = Optional(bool)
    no = Optional(bool)
    dt_shipped = Optional(datetime, default=datetime.utcnow)

sql_debug(False)