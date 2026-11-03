"""
CSRF demo (GET-based forged action) - Cyber Security IT-30001
Author: Santu Khanra

Run vulnerable:  python app.py
Run protected:   PROTECTED=1 python app.py      (Windows PowerShell: $env:PROTECTED="1"; python app.py)
"""
import os
import hmac
import secrets
from flask import (Flask, request, session, redirect, url_for,
                   render_template, abort)

app = Flask(__name__)
app.secret_key = "dev-only-secret-key"

# Switch between vulnerable and mitigated behaviour
PROTECTED = os.environ.get("PROTECTED", "0") == "1"

USERS = {
    "santu": {"password": "pass123", "email": "santu@example.com"},
}


def current_user():
    return session.get("user")


@app.route("/")
def index():
    return redirect(url_for("profile" if current_user() else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and user["password"] == password:
            session.clear()
            session["user"] = username
            # Synchronizer token: unique, unpredictable, tied to this session
            session["csrf_token"] = secrets.token_hex(32)
            return redirect(url_for("profile"))
        error = "Invalid username or password"
    return render_template("login.html", error=error, protected=PROTECTED)


@app.route("/profile")
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template(
        "profile.html",
        username=user,
        email=USERS[user]["email"],
        protected=PROTECTED,
        csrf_token=session.get("csrf_token", ""),
        message=request.args.get("msg"),
    )


@app.route("/change-email", methods=["GET", "POST"])
def change_email():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    if PROTECTED:
        # ---------- MITIGATION: anti-CSRF synchronizer token ----------
        # 1) State change only via POST
        if request.method != "POST":
            abort(403, "Blocked: state-changing request must be POST with a CSRF token.")
        # 2) Token in request must match the one stored in the server-side session
        sent = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not hmac.compare_digest(sent, expected):
            abort(403, "Blocked: missing or invalid CSRF token.")
        new_email = request.form.get("email", "").strip()
    else:
        # ---------- VULNERABLE CODE PATH ----------
        # State-changing action triggered by GET, relying only on the session
        # cookie, with no CSRF token and no check of where the request came from.
        new_email = request.args.get("email", "").strip()

    if not new_email:
        return redirect(url_for("profile", msg="No email provided"))

    USERS[user]["email"] = new_email
    return redirect(url_for("profile", msg="Email updated"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden(e):
    return f"<h2>403 Forbidden</h2><p>{e.description}</p>", 403


if __name__ == "__main__":
    print(f"Mode: {'PROTECTED (anti-CSRF token)' if PROTECTED else 'VULNERABLE'}")
    app.run(host="127.0.0.1", port=5000, debug=False)
