from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "database.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )""")
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?,?)", ("admin", "steve123"))
        except:
            pass
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
        return render_template("login.html",error="Salah!")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/")
    return render_template("dashboard.html", user=session["user"])

@app.route("/channels")
def channels():
    if "user" not in session: return redirect("/")
    return render_template("channels.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8080)
