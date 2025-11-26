from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from scheduler import start_scheduler

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "database.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )""")
        c.execute("""CREATE TABLE schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            message TEXT,
            image TEXT,
            schedule_time TEXT,
            done INTEGER DEFAULT 0
        )""")
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", ("admin", "steve123"))
        conn.commit()
        conn.close()

init_db()
start_scheduler()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Username atau password salah!")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"])

@app.route("/admin")
def admin():
    if "user" not in session or session["user"] != "admin":
        return redirect("/")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users")
    data = c.fetchall()
    conn.close()
    return render_template("admin.html", users=data)

@app.route("/add_user", methods=["POST"])
def add_user():
    if "user" not in session or session["user"] != "admin":
        return redirect("/")
    username = request.form["username"]
    password = request.form["password"]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
    except Exception:
        pass
    conn.close()
    return redirect("/admin")

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user" not in session or session["user"] != "admin":
        return redirect("/")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/post", methods=["GET","POST"])
def post():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        platform = request.form["platform"]
        message = request.form["message"]
        image = request.form.get("image","")
        schedule_time = request.form["schedule_time"]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO schedules (platform, message, image, schedule_time) VALUES (?,?,?,?)",
                  (platform, message, image, schedule_time))
        conn.commit()
        conn.close()
        return redirect("/schedule")
    return render_template("post.html")

@app.route("/schedule")
def schedule():
    if "user" not in session:
        return redirect("/")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE done = 0 ORDER BY schedule_time ASC")
    data = c.fetchall()
    conn.close()
    return render_template("schedule.html", data=data)

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE done = 1 ORDER BY schedule_time DESC")
    data = c.fetchall()
    conn.close()
    return render_template("history.html", data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
