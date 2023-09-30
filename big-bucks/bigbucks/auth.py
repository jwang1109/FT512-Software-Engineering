import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from bigbucks.global_logger import setup_global_logger, log_event,get_logger
from bigbucks.db import get_db
import logging
# 为每个视图函数创建一个日志记录器
register_logger = get_logger("register")
login_logger = get_logger("login")
password_recovery_logger = get_logger("password_recovery")
logout_logger = get_logger("logout")
bp = Blueprint("auth", __name__, url_prefix="/auth")
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db=get_db()
        g.user = (
            get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]  # Added email
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not email:  # Added email check
            error = "Email is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",  # Added email
                    (username, generate_password_hash(password), email),  # Added email
                )
                user_id = int(db.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()[0])
                db.execute("INSERT INTO accounts (user_id,balance) VALUES(?,?)",(user_id,1000000,))
                db.commit()
                register_logger.info(f"User {username} registered successfully.")

            except db.IntegrityError:
                error = f"User {username} is already registered."
                register_logger.warning(error)

            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")



@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            session["role"]= user["role"]
            if user["role"] == "admin":
                login_logger.info(f"Admin {username} logged in.")
                return redirect(url_for("symbol.admin_holdings"))
            else:
               login_logger.info(f"User {username} logged in.")
               return redirect(url_for("home.home"))

        flash(error)

    return render_template("auth/login.html")


@bp.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND email=?", (username, email))
        user = cursor.fetchone()

        if user:
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user['id']))
                db.commit()
                flash('Your password has been updated!', 'success')
                password_recovery_logger.info(f"User {username} password updated.")
                return redirect(url_for('auth.login'))
            else:
                flash('Passwords do not match', 'danger')
                password_recovery_logger.warning("Passwords do not match for password recovery.")
        else:
            flash('No account found with that username and email address.', 'danger')
            password_recovery_logger.warning("No account found for password recovery.")
    return render_template('auth/password_recovery.html')


@bp.route("/logout")
def logout():
    session.clear()
    logout_logger.info("User logged out.")
    return redirect(url_for("index"))

