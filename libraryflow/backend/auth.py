from functools import wraps
from flask import session, redirect, url_for, flash
from .models import db, User

def register_user(username, password, role='user'):
    if not username or not password:
        return {'success': False, 'message': 'Username and password required'}
    if User.query.filter_by(username=username).first():
        return {'success': False, 'message': 'Username already exists'}
    hashed, salt = User.hash_password(password)
    user = User(username=username, password=hashed, salt=salt, role=role)
    db.session.add(user); db.session.commit()
    return {'success': True}

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    hashed, _ = User.hash_password(password, user.salt)
    return user if hashed == user.password else None

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper
