from flask import Flask, render_template, request, session, redirect, url_for, flash
from .database import init_db
from .models import db, User, Book, LoanTransaction
from .auth import register_user, login_user, require_login
from datetime import datetime
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize DB
init_db(app)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        role = request.form.get('role','user')
        result = register_user(username, password, role=role)
        if result['success']:
            flash('Registered! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['message'], 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        user = login_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@require_login
def dashboard():
    user = User.query.get(session['user_id'])
    loans = LoanTransaction.query.filter_by(user_id=user.id).order_by(LoanTransaction.timestamp.desc()).all()
    books = Book.query.order_by(Book.title.asc()).all()
    return render_template('dashboard.html', user=user, books=books, loans=loans)

@app.route('/books/add', methods=['POST'])
@require_login
def add_book():
    if session.get('role') != 'admin':
        flash('Admins only', 'error')
        return redirect(url_for('dashboard'))
    title = request.form.get('title','').strip()
    author = request.form.get('author','').strip()
    copies = int(request.form.get('copies','1') or 1)
    if not title or not author:
        flash('Missing title/author', 'error'); return redirect(url_for('dashboard'))
    b = Book(title=title, author=author, copies=copies)
    db.session.add(b); db.session.commit()
    flash('Book added', 'success')
    return redirect(url_for('dashboard'))

@app.route('/borrow/<int:book_id>', methods=['POST'])
@require_login
def borrow(book_id):
    user = User.query.get(session['user_id'])
    book = Book.query.get_or_404(book_id)
    # Simple business rule "algorithm": max 5 active loans
    active_loans = LoanTransaction.query.filter_by(user_id=user.id, returned=False).count()
    if active_loans >= 5:
        flash('Borrowing limit reached (5). Return some books first.', 'error')
        return redirect(url_for('dashboard'))
    if book.copies <= 0:
        flash('No copies available.', 'error'); return redirect(url_for('dashboard'))
    loan = LoanTransaction(user_id=user.id, book_id=book.id, action='borrow', returned=False)
    book.copies -= 1
    db.session.add(loan); db.session.commit()
    flash(f'Borrowed "{book.title}"', 'success')
    return redirect(url_for('dashboard'))

@app.route('/return/<int:loan_id>', methods=['POST'])
@require_login
def return_book(loan_id):
    loan = LoanTransaction.query.get_or_404(loan_id)
    if loan.user_id != session['user_id']:
        flash('Cannot return a loan that is not yours.', 'error')
        return redirect(url_for('dashboard'))
    if loan.returned:
        flash('Already returned.', 'info'); return redirect(url_for('dashboard'))
    loan.returned = True
    loan.action = 'return'
    loan.returned_at = datetime.utcnow()
    book = Book.query.get(loan.book_id)
    book.copies += 1
    db.session.commit()
    flash('Book returned. Thank you!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
