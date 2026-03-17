import os
PORT = int(os.environ.get("PORT", 5000))
from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

from predict import predict_diet

app = Flask(__name__)
app.secret_key = "secret123"

# MYSQL CONFIG
app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE')

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)", (name,email,password))
        mysql.connection.commit()

        flash("Registered successfully")
        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user[3], password):
            session["user"] = user[1]
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
            age, bmi, diseases, activity, gender, personalized,
            include_foods, exclude_foods
        )

    return render_template("index.html", diet=diet, guide=guide, user=session["user"])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)