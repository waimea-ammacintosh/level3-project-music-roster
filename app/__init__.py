#===========================================================
# PROJECT NAME HERE
# By YOUR NAME HERE
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page - Show all notes
#-----------------------------------------------------------
@app.get("/")
def home():
    with connect_db() as db:
        sql = """
            SELECT user.id, user.first_name, user.last_name, user.email, user.role_id, role.name
            FROM user
            LEFT JOIN role 
            ON user.role_id = role.id
        """
        
        params = ()
        users = db.execute(sql, params).fetchall()

        for user in users:

            sql = """
                SELECT instrument.name
                FROM instrumentUser
                INNER JOIN instrument
                ON instrumentUser.instrument_id = instrument.id
                WHERE user_id = ?    
            """

            params = (user["id"],)
            # run query
            instruments = db.execute(sql, params).fetchall()
            user["instruments"] = instruments

        sql2 = """
            SELECT *
            FROM instrument
        """

        params2 = ()
        instruments = db.execute(sql2, params2).fetchall()

        sql3 = """
            SELECT *
            FROM role
        """

        params3 = ()
        roles = db.execute(sql3, params3).fetchall()

        return render_template("pages/home.jinja", users=users, instruments=instruments, roles = roles)


#-----------------------------------------------------------
# Handle user signup
#-----------------------------------------------------------
@app.post("/users")
def process_new_user():
    with connect_db() as db:
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name',  '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        instruments = request.form.getlist('instrument')
        role = request.form.get('role', '').strip()

        pass_hash = generate_password_hash(password)

        role_id = 0
        if(role == 'Admin'): 
            role_id = 1
        elif(role == 'Leader'): 
            role_id = 2
        else:
            role_id = 0

        if not instruments:
            flash("Please select at least one instrument", "error")
            return redirect("/")

        sql = """
            INSERT INTO user (first_name, last_name, email, pw_hash, role_id)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id;
            """
        params = (first_name, last_name, email, pass_hash, role_id)
        user = db.execute(sql, params).fetchone()
        user_id = next(iter(user.values()))

        for instrument in instruments:

            sql2 = """
                SELECT id
                FROM instrument
                WHERE name = ?
            """
            params2 = (instrument,)
            instrument = db.execute(sql2, params2).fetchone()
            instrument_id = next(iter(instrument.values()))

            sql3 = """
                INSERT INTO instrumentUser (instrument_id, user_id)
                VALUES (?,?)
            """
            params3 = (instrument_id, user_id)
            db.execute(sql3, params3)

        flash("Account created.", "success")
        return redirect("/")

#-----------------------------------------------------------
# Help page - Show some help
#-----------------------------------------------------------
@app.get("/help")
def show_help():

    flash("Test message")
    flash("Test SUCCESS message", "success")
    flash("Test INFO message", "info")
    flash("Test WARNING message", "warning")
    flash("Test ERROR message", "error")

    return render_template("pages/help.jinja")

#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)
