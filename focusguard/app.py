import json
import os
import webbrowser
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import psutil
import threading
import time

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "focusguard-demo-key-2026"

USERS_FILE = "users.json"
BLOCKED_FILE = "blocked.json"
GOALS_FILE = "goals.json"

blocking_active = False
blocking_thread = None


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


def load_blocked():
    """Load blocked apps from JSON file."""
    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE, "r") as f:
            return json.load(f)
    return []


def save_blocked(blocked):
    """Save blocked apps to JSON file."""
    with open(BLOCKED_FILE, "w") as f:
        json.dump(blocked, f, indent=2)


def load_goals():
    """Load goals from JSON file."""
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "r") as f:
            return json.load(f)
    return []


def save_goals(goals):
    """Save goals to JSON file."""
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)


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
    return render_template("focus.html")


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
    """To‑do list page (replaces original settings)."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("settings.html")


@app.route("/blocked")
def blocked_apps():
    """Blocked apps and browsers page."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("blocked.html")


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


@app.route("/verify_password", methods=["POST"])
def verify_password():
    """Endpoint used by focus mode to verify a user's password when exiting a session."""
    if "user" not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    password = request.form.get("password", "").strip()
    users = load_users()
    user = session.get("user")
    if user in users and check_password_hash(users[user], password):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid password"})

@app.route("/get_goals")
def get_goals():
    if "user" not in session:
        return jsonify([])
    return jsonify(load_goals())


@app.route("/add_goal", methods=["POST"])
def add_goal():
    if "user" not in session:
        return jsonify({"success": False})
    text = request.form.get("text", "").strip()
    desc = request.form.get("desc", "").strip()
    if not text:
        return jsonify({"success": False})
    goals = load_goals()
    goals.append({"text": text, "desc": desc, "done": False})
    save_goals(goals)
    return jsonify({"success": True, "goals": goals})


@app.route("/update_goal", methods=["POST"])
def update_goal():
    if "user" not in session:
        return jsonify({"success": False})
    idx = int(request.form.get("index", -1))
    done = request.form.get("done") == "true"
    goals = load_goals()
    if 0 <= idx < len(goals):
        goals[idx]["done"] = done
        save_goals(goals)
        # Check if all goals are completed
        all_done = len(goals) > 0 and all(g["done"] for g in goals)
        if all_done:
            save_goals([])  # Reset goals
            return jsonify({"success": True, "goals": [], "reset": True})
        return jsonify({"success": True, "goals": goals})
    return jsonify({"success": False})


@app.route("/reset_goals", methods=["POST"])
def reset_goals():
    if "user" not in session:
        return jsonify({"success": False})
    save_goals([])
    return jsonify({"success": True})


def monitor_processes(blocked_apps, duration):
    global blocking_active
    start_time = time.time()
    while blocking_active and (time.time() - start_time) < duration * 60:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(b.lower() in proc_name for b in blocked_apps):
                    proc.kill()
                    print(f"Killed blocked process: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(5)
    blocking_active = False


@app.route("/get_blocked")
def get_blocked():
    if "user" not in session:
        return jsonify([])
    return jsonify(load_blocked())


@app.route("/add_block", methods=["POST"])
def add_block():
    if "user" not in session:
        return jsonify({"success": False})
    item = request.form.get("item", "").strip()
    if not item:
        return jsonify({"success": False})
    blocked = load_blocked()
    if item not in blocked:
        blocked.append(item)
        save_blocked(blocked)
    return jsonify({"success": True, "blocked": blocked})


@app.route("/remove_block", methods=["POST"])
def remove_block():
    if "user" not in session:
        return jsonify({"success": False})
    item = request.form.get("item", "").strip()
    blocked = load_blocked()
    if item in blocked:
        blocked.remove(item)
        save_blocked(blocked)
    return jsonify({"success": True, "blocked": blocked})


@app.route("/start_blocking", methods=["POST"])
def start_blocking():
    global blocking_thread, blocking_active
    if "user" not in session:
        return jsonify({"success": False})
    duration = int(request.form.get("duration", 0))
    blocked = load_blocked()
    if not blocked or duration <= 0:
        return jsonify({"success": False})
    if blocking_thread and blocking_thread.is_alive():
        return jsonify({"success": False, "error": "Blocking already active"})
    blocking_active = True
    blocking_thread = threading.Thread(target=monitor_processes, args=(blocked, duration))
    blocking_thread.start()
    return jsonify({"success": True})


@app.route("/stop_blocking", methods=["POST"])
def stop_blocking():
    global blocking_active
    if "user" not in session:
        return jsonify({"success": False})
    blocking_active = False
    return jsonify({"success": True})


if __name__ == "__main__":
    # Open browser automatically
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
