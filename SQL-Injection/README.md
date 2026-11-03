#  SQL Injection Authentication Bypass Lab

## Safety
This project intentionally contains a vulnerable login mode for a controlled classroom demonstration. It binds to `127.0.0.1` only. Do not deploy it or expose it to a network.

## Setup on Windows
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment: `py -m venv venv`
4. Activate in PowerShell: `.\venv\Scripts\Activate.ps1`
   If blocked, use Command Prompt: `venv\Scripts\activate.bat`
5. Install packages: `py -m pip install -r requirements.txt`
6. Run: `py app.py`
7. Browse to `http://127.0.0.1:5000`

## Demo account
Username: `admin` | Password: `Admin@123`

## Pages
- `/` — overview, picks vulnerable or secure mode
- `/login?mode=vulnerable` or `/login?mode=secure` — the login form, with a toggle between modes
- `/dashboard` — shown after a successful login or a successful bypass
- `/reset` — wipes and reseeds `users.db`, useful for re-running the demo cleanly between takes

## Code to explain
- `authenticate_vulnerable()` builds SQL using string concatenation (intentionally unsafe). The login page in vulnerable mode shows the exact query that was just executed, so the audience can see the injected `'` and `--` change the query's structure.
- `authenticate_secure()` uses `?` placeholders and passes values separately, so the same payload is just treated as a literal (wrong) username.
- Both methods are selected from the same `/login` page and HTML form via the mode toggle.

## The payload
Username: `admin' --`
Password: anything

In vulnerable mode this produces:
```sql
SELECT id, username, display_name FROM users WHERE username = 'admin' --' AND password = ''
```
`--` starts a SQL comment, so everything after it (including the password check) is discarded. The query becomes "find the user named admin," which succeeds without the real password.

## Important
This is a teaching demo, not production authentication. Demo passwords are plain text to keep the SQL injection lesson focused. Real applications require salted password hashes, CSRF protection, secure session configuration and other appropriate controls.
