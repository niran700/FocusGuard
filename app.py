import json
import os
import webbrowser
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "focusguard-demo-key-2026"

USERS_FILE = "users.json"


def load_users():
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


@app.route("/")
def index():
    """Redirect to login or dashboard based on session."""
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Login page and form handler."""
    if request.method == "POST":
        user = request.form.get("user", "").strip()
        password = request.form.get("password", "").strip()

        if not user or not password:
            return render_template("login.html", error="Email/Username and password required")

        users = load_users()
        if user in users and check_password_hash(users[user], password):
            session["user"] = user
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    """Signup page and form handler."""
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not all([fullname, email, password, confirm]):
            return render_template("signup.html", error="All fields required")

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")

        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters")

        users = load_users()
        if email in users:
            return render_template("signup.html", error="Account already exists")

        users[email] = generate_password_hash(password)
        save_users(users)

        session["user"] = email
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    """Protected dashboard with user buttons."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    # Extract username from email (part before @)
    email = session["user"]
    username = email.split("@")[0] if "@" in email else email
    return render_template("dashboard.html", username=username)


@app.route("/focus")
def focus_mode():
    """Focus mode page."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return f"""
    <div style="background:#071022;color:#e6eef8;padding:40px;text-align:center;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center">
      <h1 style="font-size:28px;margin-bottom:16px">🎯 Focus Mode</h1>
      <p style="font-size:18px;color:#9aa4b2">Coming Soon</p>
      <p style="margin-top:30px"><a href="/dashboard" style="color:#7c5cff;text-decoration:underline">Back to Dashboard</a></p>
    </div>
    """


@app.route("/stats")
def stats():
    """Statistics page."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return f"""
    <div style="background:#071022;color:#e6eef8;padding:40px;text-align:center;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center">
      <h1 style="font-size:28px;margin-bottom:16px">📊 Statistics</h1>
      <p style="font-size:18px;color:#9aa4b2">Coming Soon</p>
      <p style="margin-top:30px"><a href="/dashboard" style="color:#7c5cff;text-decoration:underline">Back to Dashboard</a></p>
    </div>
    """


@app.route("/settings")
def settings():
    """Settings page."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return f"""
    <div style="background:#071022;color:#e6eef8;padding:40px;text-align:center;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center">
      <h1 style="font-size:28px;margin-bottom:16px">⚙️ Settings</h1>
      <p style="font-size:18px;color:#9aa4b2">Coming Soon</p>
      <p style="margin-top:30px"><a href="/dashboard" style="color:#7c5cff;text-decoration:underline">Back to Dashboard</a></p>
    </div>
    """


@app.route("/blocked")
def blocked_apps():
    """Blocked apps and browsers page."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return f"""
    <div style="background:#071022;color:#e6eef8;padding:40px;text-align:center;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center">
      <h1 style="font-size:28px;margin-bottom:16px">🚫 Blocked Apps & Browsers</h1>
      <p style="font-size:18px;color:#9aa4b2">Coming Soon</p>
      <p style="margin-top:30px"><a href="/dashboard" style="color:#7c5cff;text-decoration:underline">Back to Dashboard</a></p>
    </div>
    """


@app.route("/history")
def session_history():
    """Session history page."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return f"""
    <div style="background:#071022;color:#e6eef8;padding:40px;text-align:center;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center">
      <h1 style="font-size:28px;margin-bottom:16px">📝 Session History</h1>
      <p style="font-size:18px;color:#9aa4b2">Coming Soon</p>
      <p style="margin-top:30px"><a href="/dashboard" style="color:#7c5cff;text-decoration:underline">Back to Dashboard</a></p>
    </div>
    """


@app.route("/logout", methods=["POST"])
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    # Open browser automatically
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
