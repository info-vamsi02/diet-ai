import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash, g
from flask_bcrypt import Bcrypt
from predict import predict_diet

app = Flask(__name__)
app.secret_key = "secret123"

bcrypt = Bcrypt(app)

# ---------------- SQLITE DB ----------------
DATABASE = "users.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# CREATE TABLE (auto create)
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    db.commit()

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        db = get_db()

        try:
            db.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                       (name,email,password))
            db.commit()

            flash("Registered successfully")
            return redirect("/login")

        except:
            flash("Email already exists")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?",
                          (email,)).fetchone()

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user"] = user["name"]
            return redirect("/")
        else:
            flash("Invalid credentials")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- MAIN PAGE ----------------
@app.route("/", methods=["GET","POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    diet = None
    guide = None

    if request.method == "POST":

        age = request.form["age"]
        bmi = request.form["bmi"]
        gender = request.form["gender"]
        diseases = request.form.getlist("disease")
        activity = request.form["activity"]

        action = request.form.get("action")
        personalized = "yes" if action == "personalized" else None

        include_foods = request.form.get("include_foods")
        exclude_foods = request.form.get("exclude_foods")

        diet, guide = predict_diet(
            age, bmi, diseases, activity, gender,
            personalized, include_foods, exclude_foods
        )

    return render_template("index.html", diet=diet, guide=guide, user=session["user"])

# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        init_db()   # create DB automatically

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)