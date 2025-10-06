from .database import db
from datetime import datetime
import hashlib, secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(10), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        salted = (password or '') + salt
        return hashlib.sha256(salted.encode()).hexdigest(), salt

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoanTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # borrow / return
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    returned = db.Column(db.Boolean, default=False)
    returned_at = db.Column(db.DateTime)
