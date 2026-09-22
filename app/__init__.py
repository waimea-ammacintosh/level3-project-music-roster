#===========================================================
# ROSTER APP
# By AARON MACINTOSH
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *
import os
import uuid
from werkzeug.utils import secure_filename
from more_itertools import unique_justseen


UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Welcome page
#-----------------------------------------------------------
@app.get("/")
def home():

    return render_template("pages/home.jinja")


#-----------------------------------------------------------
# Login page
#-----------------------------------------------------------
@app.get("/login")
def show_login():

    return render_template("pages/login.jinja")

#-----------------------------------------------------------
# Welcome page
#-----------------------------------------------------------
@app.get("/logout")
def logout():
    session["logged_in"] = False
    session["role"] = None
    session["user"] = {}


    return redirect("/")


#-----------------------------------------------------------
# Handle user login
#-----------------------------------------------------------
@app.post("/login")
def process_login():
    with connect_db() as db:
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        

        sql = """
            SELECT email, pw_hash, first_name, last_name, id, is_admin FROM user 
            WHERE email = ?
        """
        params=(email,)
        user = db.execute(sql, params).fetchone()


        if not user:
             flash(f"Unknown user", "error")
             return redirect("/login")
 
        if not check_password_hash(user["pw_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login")
        
        sql2 = """
                SELECT week.date, week.id, instrument.name AS instrument_name
                FROM roster
                INNER JOIN week
                ON roster.week_id = week.id
                INNER JOIN instrument
                ON roster.instrument_id = instrument.id
                WHERE user_id = ?
                ORDER BY week.id ASC    
            """
        params2 = (user["id"],)
        # run query
        weeks = db.execute(sql2, params2).fetchall()

        session["logged_in"] = True
        session["is_admin"] = user.get('is_admin')
        session["user"] = {
            "id": user.get('id'),
            "first_name": user.get('first_name'),
            "last_name": user.get('last_name'),
            "email": user.get('email'),
            "weeks": weeks
            }

        flash("Signed In.", "success")

        return redirect("/")

#-----------------------------------------------------------
# Register page - Sign User Up
#-----------------------------------------------------------
@app.get("/register")
def show_register():
    with connect_db() as db:
    
        sql = """
            SELECT *
            FROM instrument
        """

        params = ()
        instruments = db.execute(sql, params).fetchall()

        sql2 = """
            SELECT *
            FROM role
        """

        params2 = ()
        roles = db.execute(sql2, params2).fetchall()

        return render_template("pages/register.jinja", instruments=instruments, roles = roles)

#-----------------------------------------------------------
# Handle user signup
#-----------------------------------------------------------
@app.post("/users/new")
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
            SELECT email FROM user
        """
        params=()
        users = db.execute(sql, params).fetchall()

        for user in users:
            if (email == user["email"]):
                flash("A user with that email already exists", "error")
                return redirect("/register")

        sql2 = """
            INSERT INTO user (first_name, last_name, email, pw_hash, role_id)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id;
            """
        params2 = (first_name, last_name, email, pass_hash, role_id)
        user = db.execute(sql2, params2).fetchone()
        user_id = next(iter(user.values()))

        for instrument in instruments:

            sql3 = """
                SELECT id
                FROM instrument
                WHERE name = ?
            """
            params3 = (instrument,)
            instrument = db.execute(sql3, params3).fetchone()
            instrument_id = next(iter(instrument.values()))

            sql4 = """
                INSERT INTO instrumentUser (instrument_id, user_id)
                VALUES (?,?)
            """
            params4 = (instrument_id, user_id)
            db.execute(sql4, params4)

        sql5 = """
            SELECT email, pw_hash, first_name, last_name, id, user.is_admin, role.name FROM user 
            WHERE user.id = ?
        """
        params5 = (user_id,)
        user_data = db.execute(sql5, params5).fetchone()

        sql = """
                SELECT week.date, week.id, instrument.name AS instrument_name
                FROM roster
                INNER JOIN week
                ON roster.week_id = week.id
                INNER JOIN instrument
                ON roster.instrument_id = instrument.id
                WHERE user_id = ?
                ORDER BY week.id ASC    
            """
        params = (user["id"],)
        # run query
        weeks = db.execute(sql, params).fetchall()

        session["logged_in"] = True
        session["is_admin"] = user_data.get('is_admin')
        session["user"] = {
            "id": user_data.get('id'),
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "email": user_data.get('email'),
            "weeks": weeks
            }


        flash("Account created.", "success")
        return redirect("/")

#-----------------------------------------------------------
# Roster Page - Shows full roster
#-----------------------------------------------------------
@app.get("/roster")
def show_roster():
    with connect_db() as db:
        sql = """
            SELECT
                instrument.id AS i_id,
                user.first_name AS u_fname,
                user.last_name AS u_lname
            FROM week
            CROSS JOIN instrument

            LEFT JOIN roster
            ON roster.week_id = week.id
            AND roster.instrument_id = instrument.id
   
            LEFT JOIN user
            ON user.id = roster.user_id
    
            ORDER BY week.date ASC, instrument.name ASC
        """
        params = ()
        roster = db.execute(sql, params).fetchall()
        print(roster)

        sql2 = """
            SELECT date FROM week
        """        
        params2 = ()
        weeks = db.execute(sql2, params2).fetchall()

        sql3 = """
            SELECT name, id FROM instrument
        """
        params3=()
        instruments = db.execute(sql3, params3).fetchall()

        return render_template("pages/roster.jinja", roster=roster, instruments=instruments, weeks=weeks)

#-----------------------------------------------------------
# Submit unavailability Page - Form to submit unavailability
#-----------------------------------------------------------
@app.get("/unavailability")
def show_unavailability_form():
    with connect_db() as db:
        sql = """
            SELECT
                user.first_name AS u_fname,
                user.id AS u_id,
                week.id AS w_id,
                week.date,
                unavailability.completed
            FROM unavailability
            JOIN week ON week.id = unavailability.week_id
            JOIN user ON user.id = unavailability.user_id

            WHERE user.id =? AND unavailability.completed = FALSE
            
            ORDER BY w_id ASC            
        """
        params = (session['user']['id'],)
        weeks = db.execute(sql, params).fetchall()

        return render_template("pages/submit-unavailability.jinja", weeks=weeks)


#-----------------------------------------------------------
# Handle unavailability form
#-----------------------------------------------------------
@app.post("/unavailability")
def process_unavailability():
    with connect_db() as db:
        submitted_weeks = request.form.getlist('weeks')
        submitted_weeks = [int(week) for week in submitted_weeks]

        sql = """
                    SELECT
                        week.id
                    FROM unavailability
                    JOIN week ON week.id = unavailability.week_id
                    JOIN user ON user.id = unavailability.user_id
        
                    WHERE user.id =? AND unavailability.completed = FALSE
                    
                    ORDER BY week.id ASC            
                """
        params = (session['user']['id'],)
        weeks = db.execute(sql, params).fetchall()

        for week in submitted_weeks:
            for i in weeks:
                if week == i['id']:
                    weeks.remove(i)

            sql2 = """
                UPDATE unavailability
                SET completed = TRUE, available = FALSE
                WHERE week_id =?
            """
            params2=(week,)
            db.execute(sql2, params2)

        for week in weeks:
            sql3="""
                SELECT id FROM week
                WHERE date =?
            """
            params3=(week.date,)
            week_id = db.execute(sql3, params3).fetchone()
            
            sql4 = """
                UPDATE unavailability
                SET completed = TRUE, available = TRUE
                WHERE week_id =?
            """
            params4=(week_id,)
            db.execute(sql4, params4)
      
    flash('Submitted', 'success')
    return redirect("/")


#-----------------------------------------------------------
# Individual Week Page - Shows details for one week
#-----------------------------------------------------------
@app.get("/week/<int:id>")
def show_week(id):
    with connect_db() as db:
        sql = """
            SELECT
                instrument.id AS i_id,
                user.first_name AS u_fname,
                user.last_name AS u_lname
            FROM week
            CROSS JOIN instrument

            LEFT JOIN roster
            ON roster.week_id = week.id
            AND roster.instrument_id = instrument.id
   
            LEFT JOIN user
            ON user.id = roster.user_id

            WHERE week.id=?
            ORDER BY week.date ASC, instrument.name ASC
        """
        params = (id,)
        week = db.execute(sql, params).fetchall()

        sql2="""
            SELECT date, practice_date FROM week
            WHERE id=?
        """
        params2=(id,)
        week_data = db.execute(sql2, params2).fetchone()

        sql3 = """
            SELECT name, id FROM instrument
        """
        params3=()
        instruments = db.execute(sql3, params3).fetchall()

        sql4="""
            SELECT filename, week_id FROM file
            WHERE week_id=?
        """
        params4=(id,)
        files = db.execute(sql4, params4).fetchall()

        sql5 = """
            SELECT user_id FROM roster
            WHERE instrument_id = '1' AND week_id=?
        """
        params5=(id,)
        worship_leader = db.execute(sql5, params5).fetchone()

        return render_template("pages/week-page.jinja", week=week, instruments=instruments, week_data=week_data, files=files, worship_leader=worship_leader, week_id=id)

#-----------------------------------------------------------
# New File Upload - handles new file upload form
#-----------------------------------------------------------
@app.post("/newfile/week/<int:id>")
def add_file(id):
    # Get the file selected via the form
    file = request.files.get('file', None)
    if not file or file.filename == '':
        flash("There was a problem uploading the file", "error")
        return redirect("/new/creature")

    # Sanitise filename and make it unique
    filename = secure_filename(file.filename)
    random_prefix = uuid.uuid4().hex[:12]
    unique_filename = f"{random_prefix}_{filename}"

    # Get the path of the upload folder
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save file to disk
    file.save(filepath)

    # Add the form data and the upload filename to the DB
    with connect_db() as db:
        sql = "INSERT INTO file (filename, week_id) VALUES (?, ?)"
        params = (unique_filename, id)
        db.execute(sql, params)

        flash(f"{filename} added", "success")
        return redirect(url_for('show_week', id=id))

#-----------------------------------------------------------
# User List page - show all users
#-----------------------------------------------------------
@app.get("/users/show")
def show_users():
    with connect_db() as db:
        sql = """
            SELECT user.id, user.first_name, user.last_name, user.email, user.is_admin
            FROM user
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

        return render_template("pages/user-list.jinja", users=users, instruments=instruments)


#-----------------------------------------------------------
# Submit Request Page - shows submit request form
#-----------------------------------------------------------
@app.get("/request")
def show_request():

    weeks = list(unique_justseen(session['user']['weeks'], key = 'id'))

    return render_template("pages/request.jinja", weeks=weeks)

#-----------------------------------------------------------
# Handle Request form
#-----------------------------------------------------------
@app.post("/request")
def process_request():
    with connect_db() as db:
        week = request.form.get('week').strip()
        message = request.form.get('message', '').strip()


        if message:
            sql = """
                INSERT INTO request (week_id, user_id, message) VALUES (?, ?, ?)
            """
            params=(week, session['user']['id'], message )
            db.execute(sql, params)
        else:
            sql = """
                INSERT INTO request (week_id, user_id, message) VALUES (?, ?, ?)
            """
            params=(week, session['user']['id'], 'No Message')
            db.execute(sql, params)

      
    flash('Submitted request', 'success')
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
