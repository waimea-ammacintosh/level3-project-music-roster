#===========================================================
# ROSTER APP
# By AARON MACINTOSH
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


    return render_template("pages/home.jinja")


#-----------------------------------------------------------
# Handle user login
#-----------------------------------------------------------
@app.post("/login")
def process_login():
    with connect_db() as db:
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        

        sql = """
            SELECT user.email, user.pw_hash, user.first_name, user.last_name, user.id, user.role_id, role.name FROM user 
            INNER JOIN role 
            ON user.role_id = role.id
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
        
        sql = """
                SELECT week.date, instrument.name
                FROM roster
                INNER JOIN week
                ON roster.week_id = week.id
                INNER JOIN instrument
                ON roster.instrument_id = instrument.id
                WHERE user_id = ?    
            """
        params = (user["id"],)
        # run query
        weeks = db.execute(sql, params).fetchall()

        session["logged_in"] = True
        session["role"] = user.get('name')
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
# Roster Page - Shows full roster
#-----------------------------------------------------------
@app.get("/roster")
def show_roster():
    with connect_db() as db:
    
        sql = """
            SELECT user.first_name, user.last_name, week.date, week.id, instrument.name
            FROM roster
            INNER JOIN user
            ON roster.user_id = user.id
            INNER JOIN week
            ON roster.week_id = week.id
            INNER JOIN instrument
            ON roster.instrument_id = instrument.id
            ORDER BY week.id ASC
        """

        params = ()
        rosters = db.execute(sql, params).fetchall()

        sql2 = """
            SELECT date FROM week
        """
        
        params2 = ()
        weeks = db.execute(sql2, params2).fetchall()

        roster = []
        target_key = 'date'
        prev_week_id = 0

        for week in weeks:
            
            target_id = week.get('date')           
            for d in reversed(rosters):
                if d.get(target_key) == target_id:                    
                    last_index = d.id
                    break

            week_data = []
            for i in rosters:

                if i.get('id') < prev_week_id:
                    continue
                elif i != rosters[last_index+1]:
                    week_data.append(i)
                    print(week_data)
                    print()
                elif i == rosters[last_index+1]:
                    week_data.append(i)
                    roster.append(week_data)
                    print(week_data)
                    print()
                    week_data.clear()
                    break
            prev_week_id = last_index
        print(roster)
            


            

        

        return render_template("pages/roster.jinja", roster=roster)


#-----------------------------------------------------------
# User List page - show all users
#-----------------------------------------------------------
@app.get("/users/show")
def show_users():
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

        return render_template("pages/user-list.jinja", users=users, instruments=instruments)

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
            SELECT user.email, user.pw_hash, user.first_name, user.last_name, user.id, user.role_id, role.name FROM user 
            INNER JOIN role 
            ON user.role_id = role.id
            WHERE user.id = ?
        """
        params5 = (user_id,)
        user_data = db.execute(sql5, params5).fetchone()

        sql = """
                SELECT week.date, instrument.name
                FROM roster
                INNER JOIN week
                ON roster.week_id = week.id
                INNER JOIN instrument
                ON roster.instrument_id = instrument.id
                WHERE user_id = ?    
            """
        params = (user["id"],)
        # run query
        weeks = db.execute(sql, params).fetchall()

        session["logged_in"] = True
        session["role"] = user_data.get('name')
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
