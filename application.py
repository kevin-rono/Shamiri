import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shamiri.db")


@app.route("/")
def index():
    # return homepage
    return render_template("index.html")


@app.route("/about")
def about():
    # return about page
    return render_template("about.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    # Get username
    username = request.args.get("username")

    # Check for username
    if not len(username) or db.execute("SELECT 1 FROM users1 WHERE username = :username", username=username.lower()):
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/eligibility", methods=["GET", "POST"])
@login_required
def eligibility():
    if request.method == "POST":
        # ensure fields are submitted
        if not request.form.get("name"):
            return apology("Must provide name")
        if not request.form.get("gender"):
            return apology("Must provide gender")
        if not request.form.get("age"):
            return apology("Must provide age")
        if not request.form.get("year"):
            return apology("Must provide year")

        # ensure score values are checked and added
        sum = 0
        for question in ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]:
            value = request.form.get(question)
            if not value:
                return apology("Must check all boxes")
            sum += int(value)
        print(sum)

        # new table
        db.execute("INSERT INTO form (gender, age, school, id, name, score, email) VALUES(:gender, :age, :school, :id, :name, :score, :email)",
                   gender=request.form.get("gender"), age=request.form.get("age"), school=request.form.get("year"), id=session["user_id"], name=request.form.get("name"), score=sum, email=request.form.get("email"))

        flash("Your response was recorded! Now just wait as one of the administrators will reach out to you.")

        # return frequently asked questions page
        return redirect("/FAQ")

    else:
        return render_template("eligibility.html")


@app.route("/record", methods=["GET"])
def get_record():
    # display contents from form table
    participants = db.execute("SELECT * FROM form")
    return render_template("filled.html", participants=participants)


@app.route("/answer", methods=["GET"])
def get_answer():
    # display content from answers table
    participants = db.execute("SELECT * FROM answers")
    return render_template("answer.html", participants=participants)


@app.route("/intervention", methods=["GET", "POST"])
@login_required
def intervention():
    if request.method == "POST":
        # ensure all questions are answered
        if not request.form.get("growth"):
            return apology("Please answer all the questions in the spaces provided!")
        if not request.form.get("values"):
            return apology("Please answer all the questions in the spaces provided!")

        # insert answers into table
        db.execute("INSERT INTO answers (id, growth, affirmation) VALUES(:id, :growth, :affirmation)",
                   id=session["user_id"], affirmation=request.form.get("values"), growth=request.form.get("growth"))

        flash("Your response was recorded! Now wait as we evaluate your progress before reaching out to you with feedback")

        # return intervention page
        return redirect("/intervention")

    else:
        return render_template("intervention.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users1 WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Check whether admin
        capacity = db.execute("SELECT admin FROM users1 WHERE id = :id", id=session["user_id"])

        # if user redirect to homepage
        place = capacity[0]["admin"]
        if place == 0:
            return redirect("/")
        # if admin redirect to record page
        else:
            return redirect("/record")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/FAQ", methods=["GET", "POST"])
def FAQ():
    # display Frequently Asked Questions Page
    return render_template("faq.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register the user."""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("Missing confirmation", 400)

        # Ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and Confirmation do not match")

        # Hash password
        hashed = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Add user to database
        result = db.execute("INSERT INTO users1 (username, hash, admin) VALUES (:username, :hash, :admin)",
                            username=request.form.get("username"), hash=hashed, admin=0)
        if not result:
            return apology("Username not available")

        # log them in
        session["user_id"] = result

        flash("Registered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Register the admin."""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("Missing confirmation", 400)

        # Ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and Confirmation do not match")

        # Hash password
        hashed = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Add user to database
        result = db.execute("INSERT INTO users1 (username, hash, admin) VALUES (:username, :hash, :admin)",
                            username=request.form.get("username"), hash=hashed, admin=1)
        if not result:
            return apology("Username not available")

        # log them in
        session["user_id"] = result

        flash("Registered as Admin!")

        # Redirect user to record page
        return redirect("/record")

    # User reached route via GET
    else:
        return render_template("admin.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    # display contact page
    return render_template("contact.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)