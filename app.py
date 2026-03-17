import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash,  g
from flask_bcrypt import Bcrypt
from predict import predict_diet

app = Flask(__name__)
app.secret_key = "secret123"


bcrypt = Bcrypt(app)

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

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields required")
            return render_template("register.html")

        password = bcrypt.generate_password_hash(password).decode("utf-8")

        db = get_db()

        try:
            db.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                       (name,email,password))
            db.commit()
            flash("Registered successfully")
            return redirect("/login")

        except sqlite3.IntegrityError:
            flash("Email already exists")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?",
                          (email,)).fetchone()

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user"] = user["name"]
            return redirect("/")
        else:
            flash("Invalid credentials")

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# MAIN PAGE
@app.route("/", methods=["GET","POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    diet = None
    guide = None

    if request.method == "POST":
        try:
            age = request.form.get("age", "0")
            bmi = request.form.get("bmi", "0")
            gender = request.form.get("gender", "Male")
            diseases = request.form.getlist("disease") or []
            activity = request.form.get("activity", "Low")

            action = request.form.get("action")
            personalized = "yes" if action == "personalized" else None

            include_foods = request.form.get("include_foods", "")
            exclude_foods = request.form.get("exclude_foods", "")

            # 🔥 SAFE CALL
            try:
                diet, guide = predict_diet(
                    age, bmi, diseases, activity, gender,
                    personalized, include_foods, exclude_foods
                )
            except Exception as e:
                print("PREDICT ERROR:", e)

                # fallback (never crash)
                diet = "Balanced"
                guide = {
                    "calories": "2000 kcal",
                    "protein": "70g",
                    "carbohydrates": "250g",
                    "fat": "60g",
                    "vitamins": "Basic",
                    "recommended_foods": ["Rice","Fruits"],
                    "foods_to_avoid": ["Junk"]
                }

        except Exception as e:
            print("FORM ERROR:", e)

    return render_template("index.html", diet=diet, guide=guide, user=session["user"])

if __name__ == "__main__":
    with app.app_context():
        init_db()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)