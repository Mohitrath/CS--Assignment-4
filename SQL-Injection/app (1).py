from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-demo-key-before-real-use"
DB = Path(__file__).with_name("users.db")
LAST_QUERY = {"text": ""}  # kept only so the UI can show what was actually run, for teaching purposes

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        display_name TEXT NOT NULL
    )""")
    con.execute("INSERT OR IGNORE INTO users(username,password,display_name) VALUES(?,?,?)",
                ("admin", "Admin@123", "Administrator"))
    con.execute("INSERT OR IGNORE INTO users(username,password,display_name) VALUES(?,?,?)",
                ("student", "Student@123", "Demo Student"))
    con.commit()
    con.close()

def authenticate_vulnerable(username, password):
    # INTENTIONALLY VULNERABLE: never build SQL this way in a real application.
    query = ("SELECT id, username, display_name FROM users "
             f"WHERE username = '{username}' AND password = '{password}'")
    LAST_QUERY["text"] = query
    con = db()
    try:
        return con.execute(query).fetchone()
    finally:
        con.close()

def authenticate_secure(username, password):
    # SECURE DEMO: values are supplied separately from the SQL statement.
    query = """SELECT id, username, display_name FROM users
               WHERE username = ? AND password = ?"""
    con = db()
    try:
        return con.execute(query, (username, password)).fetchone()
    finally:
        con.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    mode = request.args.get("mode", "vulnerable")
    if request.method == "POST":
        mode = request.form.get("mode", "secure")
        if mode not in ("vulnerable", "secure"):
            mode = "secure"
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        try:
            user = (authenticate_vulnerable(username, password) if mode == "vulnerable"
                    else authenticate_secure(username, password))
            if user:
                session["display_name"] = user["display_name"]
                session["login_mode"] = mode
                flash("Authentication accepted.", "success")
                return redirect(url_for("dashboard"))
            flash("Authentication rejected. No matching account was found.", "error")
        except sqlite3.Error:
            app.logger.exception("Database error in local classroom demonstration")
            flash("The database rejected the request. See the server terminal.", "error")
    if mode not in ("vulnerable", "secure"):
        mode = "vulnerable"
    return render_template("login.html", mode=mode, last_query=LAST_QUERY["text"])

@app.route("/reset")
def reset():
    # Wipes and reseeds the demo database, so the lab can be re-run cleanly between takes.
    if DB.exists():
        DB.unlink()
    init_db()
    flash("Demo database reset to its original state.", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "display_name" not in session:
        return redirect(url_for("home"))
    return render_template("dashboard.html",
        display_name=session["display_name"],
        mode=session.get("login_mode", "unknown"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    # Localhost only: do not expose this intentionally vulnerable lab.
    app.run(host="127.0.0.1", port=5000, debug=False)
