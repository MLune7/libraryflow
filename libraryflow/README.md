# LibraryFlow (Flask + SQLite)

A tiny library lending app that mirrors the *algorithms and flow* of your bank app (register/login with salted hashing, account-like entity (Book) with balance-like field (copies), and a transaction log (LoanTransaction)).

## Run (dev)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
export FLASK_APP=app.py && python -m flask run  # or python app.py
```
The app stores data in `../data/library.db`.

## Structure
```
backend/
  app.py, models.py, database.py, auth.py, requirements.txt
frontend/
  templates/ (Jinja2 templates)
  static/css, static/js
data/ library.db (created on first run)
logs/ (sample scan logs)
report_assets/ (images used in the report)
```

> Note: This project ships **secure-by-default**. The report includes *non-executable* before/after code *images* explaining common mistakes (SQL injection, XSS) and how they were prevented.
