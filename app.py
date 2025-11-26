from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

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
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", ("admin", "steve123"))
        conn.commit()
        conn.close()

init_db()

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
            return redirect("/admin")
        else:
            return render_template("login.html", error="Username atau password salah!")
    return render_template("login.html")

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
    except:
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
