from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "database.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    new = not os.path.exists(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    if new:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", ("admin","steve123"))
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]; p=request.form["password"]
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
        user=c.fetchone(); conn.close()
        if user:
            session["user"]=u
            return redirect("/dashboard")
        return render_template("login.html", error="Username atau password salah!")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/")
    return render_template("dashboard.html", user=session["user"])

@app.route("/channels")
def channels():
    if "user" not in session: return redirect("/")
    return render_template("channels.html")

# FILE MANAGER
@app.route("/files")
def files_page():
    if "user" not in session:
        return redirect("/")
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("files.html", files=files)

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "user" not in session:
        return redirect("/")
    if "file" not in request.files:
        return redirect("/files")
    f = request.files["file"]
    if f.filename == "":
        return redirect("/files")
    filename = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return redirect("/files")

@app.route("/delete_file/<name>")
def delete_file(name):
    if "user" not in session:
        return redirect("/")
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, name))
    except:
        pass
    return redirect("/files")

# ADMIN USER SETTINGS
@app.route("/admin")
def admin_page():
    if "user" not in session or session["user"]!="admin":
        return redirect("/")
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    c.execute("SELECT id, username FROM users")
    users=c.fetchall()
    conn.close()
    return render_template("admin.html", users=users)

@app.route("/add_user", methods=["POST"])
def add_user():
    if "user" not in session or session["user"]!="admin": return redirect("/")
    u=request.form["username"]; p=request.form["password"]
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)",(u,p))
        conn.commit()
    except: pass
    conn.close()
    return redirect("/admin")

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user" not in session or session["user"]!="admin": return redirect("/")
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    c.execute("DELETE FROM users WHERE id=?",(user_id,))
    conn.commit(); conn.close()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
