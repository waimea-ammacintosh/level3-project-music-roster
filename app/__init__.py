# ===========================================================
# ROSTER APP
# By AARON MACINTOSH
# ===========================================================

# Imports
from flask import (
    Flask,
    request,
    session,
    render_template,
    flash,
    redirect,
    send_file,
    make_response,
    url_for,
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *
from app.helpers.auth import admin_required
import os
import uuid
from werkzeug.utils import secure_filename
from more_itertools import unique_justseen, unique_everseen
from collections import defaultdict
from pandas import to_datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta, SU

# Uploads folder path
UPLOAD_FOLDER = os.path.join("app", "static", "uploads")


# Create the app
app = Flask(__name__)


# ===========================================================
# App Routes Handlers
# ===========================================================


# -----------------------------------------------------------
# Welcome page
# -----------------------------------------------------------
@app.get("/")
def home():
    # if there is no session, create a logged out one
    if not bool(session):
        session["logged_in"] = False
        session["user"] = {}
        session["is_admin"] = False

    # select requests if the user is an admin, else don't as they are not required
    if session["is_admin"]:
        with connect_db() as db:

            sql = """
                SELECT user.first_name, user.id AS u_id, week.id AS w_id, user.last_name, week.date
                FROM request
                INNER JOIN user
                ON user_id = user.id
                INNER JOIN week
                ON week_id = week.id
            """
            params = ()
            requests = db.execute(sql, params).fetchall()
    else:
        requests = None

    # remake the weeks part of the session, in case it has changed since the last time they opened the app if they are logged in
    if session["logged_in"]:
        with connect_db() as db:
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
            params2 = (session["user"]["id"],)
            # run query
            weeks_data = db.execute(sql2, params2).fetchall()
            sql3 = """
                SELECT roster.week_id, week.date FROM roster
                LEFT JOIN week ON roster.week_id = week.id 
                WHERE user_id=? 
            """
            params3 = (session["user"]["id"],)
            week_ids = db.execute(sql3, params3).fetchall()

            # delete duplicate weeks
            unique_week_ids = list(unique_justseen(week_ids))
            weeks = []
            for i in unique_week_ids:
                week_instruments = []
                week_data = {}
                for week in weeks_data:
                    if week["id"] == i["week_id"]:
                        week_instruments.append(week["instrument_name"])
                week_data["id"] = i["week_id"]
                week_data["instruments"] = week_instruments
                week_data["date"] = i["date"]
                weeks.append(week_data)

            session["user"]["weeks"] = weeks

    # ---------------------------------------------
    # Delete past stuff
    with connect_db() as db:
        # make sure foreign key logic is allowed
        sql4 = "PRAGMA foreign_keys = ON"
        db.execute(sql4)
        # get date for deleting (-1, as this will delete the day only if the day has finished)
        current_date = datetime.now() - timedelta(days=1)
        print(current_date)

        # get all dates to delete
        sql5 = """
            SELECT date, id FROM week WHERE date < ?
        """
        params5 = (current_date,)
        weeks_to_delete = db.execute(sql5, params5).fetchall()
        print(weeks_to_delete)

        # delete files related to the weeks
        for week in weeks_to_delete:
            # get files
            sql6 = """
                SELECT filename FROM file WHERE week_id = ? 
            """
            params6 = (week["id"],)
            files = db.execute(sql6, params6).fetchall()
            # delete files
            for file in files:
                file_name = file["filename"]
                # Get the path of the file
                filepath = os.path.join(UPLOAD_FOLDER, file_name)
                # Delete file from disk if it exists
                if os.path.exists(filepath):
                    os.remove(filepath)

            # delete records from db
            sql7 = """
                DELETE FROM file WHERE week_id = ?
            """
            params7 = (week["id"],)
            db.execute(sql7, params7)

        # delete week, then changes will cascade
        sql8 = """
            DELETE FROM week WHERE date <?
        """
        params8 = (current_date,)
        db.execute(sql8, params8)

    return render_template("pages/home.jinja", requests=requests)


# -----------------------------------------------------------
# Login page
# -----------------------------------------------------------
@app.get("/login")
def show_login():

    return render_template("pages/login.jinja")


# -----------------------------------------------------------
# sign out route
# -----------------------------------------------------------
@app.get("/logout")
def logout():
    # clear session
    session["logged_in"] = False
    session["user"] = {}
    session["is_admin"] = False

    return redirect("/")


# -----------------------------------------------------------
# Handle user login
# -----------------------------------------------------------
@app.post("/login")
def process_login():
    with connect_db() as db:
        # get and sanitize the form data
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        # select user data
        sql = """
            SELECT email, pw_hash, first_name, last_name, id, is_admin FROM user 
            WHERE email = ?
        """
        params = (email,)
        user = db.execute(sql, params).fetchone()

        # check if correct email is inputted
        if not user:
            flash(f"Unknown user", "error")
            return redirect("/login")

        # check if correct password is inputted
        if not check_password_hash(user["pw_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login")

        # collect week data linked to the user
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
        weeks_data = db.execute(sql2, params2).fetchall()

        sql3 = """
            SELECT roster.week_id, week.date FROM roster
            LEFT JOIN week ON roster.week_id = week.id 
            WHERE user_id=? 
        """
        params3 = (user["id"],)
        week_ids = db.execute(sql3, params3).fetchall()

        # delete duplicate weeks
        unique_week_ids = list(unique_justseen(week_ids))
        weeks = []
        for i in unique_week_ids:
            week_instruments = []
            week_data = {}
            for week in weeks_data:
                if week["id"] == i["week_id"]:
                    week_instruments.append(week["instrument_name"])
            week_data["id"] = i["week_id"]
            week_data["instruments"] = week_instruments
            week_data["date"] = i["date"]
            weeks.append(week_data)

        # create session
        session["logged_in"] = True
        session["user"] = {
            "id": user.get("id"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
            "weeks": weeks,
        }
        session["is_admin"] = user.get("is_admin")

        flash("Signed In.", "success")

        return redirect("/")


# -----------------------------------------------------------
# Register page - Sign User Up
# -----------------------------------------------------------
@app.get("/register")
def show_register():
    with connect_db() as db:

        # get all instruments for form
        sql = """
            SELECT *
            FROM instrument
        """
        params = ()
        instruments = db.execute(sql, params).fetchall()

        return render_template("pages/register.jinja", instruments=instruments)


# -----------------------------------------------------------
# Handle user signup
# -----------------------------------------------------------
@app.post("/users/new")
def process_new_user():
    with connect_db() as db:

        # get and sanitize the form data
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        instruments = request.form.getlist("instrument")
        role = request.form.get("role", "").strip()

        # check wether user is admin
        is_admin = False
        if role == "Admin":
            is_admin = True

        pass_hash = generate_password_hash(password)

        if not instruments:
            flash("Please select at least one instrument", "error")
            return redirect("/")

        sql = """
            SELECT email FROM user
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        for user in users:
            if email == user["email"]:
                flash("A user with that email already exists", "error")
                return redirect("/register")

        sql2 = """
            INSERT INTO user (first_name, last_name, email, pw_hash, is_admin)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id;
            """
        params2 = (first_name, last_name, email, pass_hash, is_admin)
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
            SELECT id FROM week
        """
        params5 = ()
        all_weeks = db.execute(sql5, params5).fetchall()

        for week in all_weeks:
            sql6 = """
                INSERT INTO unavailability (user_id, week_id, available, completed)
                VALUES (?, ?, False, False)
            """
            params6 = (user_id, week["id"])
            db.execute(sql6, params6)

        sql7 = """
            SELECT email, pw_hash, first_name, last_name, id, is_admin
            FROM user 
            WHERE user.id = ?
        """
        params7 = (user_id,)
        user_data = db.execute(sql7, params7).fetchone()

        sql8 = """
                SELECT week.date, week.id, instrument.name AS instrument_name
                FROM roster
                INNER JOIN week
                ON roster.week_id = week.id
                INNER JOIN instrument
                ON roster.instrument_id = instrument.id
                WHERE user_id = ?
                ORDER BY week.id ASC    
            """
        params8 = (user["id"],)
        # run query
        weeks_data = db.execute(sql8, params8).fetchall()

        sql9 = """
            SELECT roster.week_id, week.date FROM roster
            LEFT JOIN week ON roster.week_id = week.id 
            WHERE user_id=? 
        """
        params9 = (user["id"],)
        week_ids = db.execute(sql9, params9).fetchall()

        # delete duplicate weeks
        unique_week_ids = list(unique_justseen(week_ids))
        weeks = []
        for i in unique_week_ids:
            week_instruments = []
            week_data = {}
            for week in weeks_data:
                if week["id"] == i["week_id"]:
                    week_instruments.append(week["instrument_name"])
            week_data["id"] = i["week_id"]
            week_data["instruments"] = week_instruments
            week_data["date"] = i["date"]
            weeks.append(week_data)

        session["logged_in"] = True
        session["user"] = {
            "id": user_data.get("id"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "email": user_data.get("email"),
            "weeks": weeks,
        }
        session["is_admin"] = user_data.get("is_admin")

        flash("Account created.", "success")
        return redirect("/")


# -----------------------------------------------------------
# Roster Page - Shows full roster
# -----------------------------------------------------------
@app.get("/roster")
@login_required
def show_roster():
    with connect_db() as db:
        # get roster data
        sql = """
            SELECT
                instrument.id AS i_id,
                user.first_name AS u_fname,
                user.last_name AS u_lname,
                week.date
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

        sql2 = """
            SELECT date FROM week
        """
        params2 = ()
        weeks = db.execute(sql2, params2).fetchall()

        # adding a table id (groups of 4 weeks) to the weeks, for display on the page
        table_id = 1
        weeks_gone = 1
        for week in weeks:
            # has 5 weeks gone
            if weeks_gone < 4:
                # not yet, so add table id, add one to weeks gone, and continue
                week["table_id"] = table_id
                weeks_gone += 1
            else:
                # yes, so add table id, reset how many weeks have passed, and add one to table group id
                week["table_id"] = table_id
                weeks_gone = 1
                table_id += 1

        # how many tables to display on page
        num_tables = unique_everseen(d["table_id"] for d in weeks)

        # add table_id to roster entries
        for entry in roster:
            for week in weeks:
                if entry["date"] == week["date"]:
                    entry["table_id"] = week["table_id"]

        # get instrument names
        sql3 = """
            SELECT name, id FROM instrument
        """
        params3 = ()
        instruments = db.execute(sql3, params3).fetchall()

        return render_template(
            "pages/roster-show.jinja",
            roster=roster,
            instruments=instruments,
            weeks=weeks,
            num_tables=num_tables,
        )


# -----------------------------------------------------------
# Submit unavailability Page - Form to submit unavailability
# -----------------------------------------------------------
@app.get("/unavailability")
@login_required
def show_unavailability_form():
    with connect_db() as db:
        # select weeks the user hasn't filled out yet
        sql = """
            SELECT
                week.id AS w_id,
                week.date,
                unavailability.completed
            FROM unavailability
            JOIN week ON week.id = unavailability.week_id
            JOIN user ON user.id = unavailability.user_id

            WHERE user.id =? AND unavailability.completed = FALSE
            
            ORDER BY w_id ASC            
        """
        params = (session["user"]["id"],)
        weeks = db.execute(sql, params).fetchall()

        return render_template("pages/submit-unavailability.jinja", weeks=weeks)


# -----------------------------------------------------------
# Handle unavailability form
# -----------------------------------------------------------
@app.post("/unavailability")
@login_required
def process_unavailability():
    with connect_db() as db:
        # get data from form
        submitted_weeks = request.form.getlist("weeks")
        unavailable_weeks = [int(week) for week in submitted_weeks]

        # select all weeks that were in the form, to update later
        sql = """
                    SELECT
                        week.id,
                        week.date
                    FROM unavailability
                    JOIN week ON week.id = unavailability.week_id
                    JOIN user ON user.id = unavailability.user_id
        
                    WHERE user.id =? AND unavailability.completed = FALSE
                    
                    ORDER BY week.id ASC            
                """
        params = (session["user"]["id"],)
        weeks = db.execute(sql, params).fetchall()

        # set all weeks to completed and true, later we will update the unavailable dates to be unavailable
        for week in weeks:
            sql3 = """
                UPDATE unavailability
                SET completed = TRUE, available = TRUE
                WHERE week_id =? AND user_id=?
            """
            params3 = (week["id"], session["user"]["id"])
            db.execute(sql3, params3)

        # update weeks said to be unavailable to be unavailable
        for week in unavailable_weeks:
            print(week)

            sql2 = """
                UPDATE unavailability
                SET completed = TRUE, available = FALSE
                WHERE week_id =? AND user_id =?
            """
            params2 = (week, session["user"]["id"])
            db.execute(sql2, params2)

        # get first and last weeks for flash
        first_week = weeks[0]["date"]
        last_week = weeks[-1]["date"]

    flash(f"Submitted unavailability between {first_week} and {last_week}", "success")
    return redirect("/")


# -----------------------------------------------------------
# Individual Week Page - Shows details for one week
# -----------------------------------------------------------
@app.get("/week/<int:id>")
@login_required
def show_week(id):
    with connect_db() as db:
        # get data about users on one week
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

        # get data about the date
        sql2 = """
            SELECT date, practice_date FROM week
            WHERE id=?
        """
        params2 = (id,)
        week_data = db.execute(sql2, params2).fetchone()

        # get instrument data
        sql3 = """
            SELECT name, id FROM instrument
        """
        params3 = ()
        instruments = db.execute(sql3, params3).fetchall()

        # get file data
        sql4 = """
            SELECT filename, week_id, id FROM file
            WHERE week_id=?
        """
        params4 = (id,)
        files = db.execute(sql4, params4).fetchall()

        # is the user a the worship leader for this week
        sql5 = """
            SELECT user_id FROM roster
            WHERE instrument_id = '1' AND week_id=?
        """
        params5 = (id,)
        worship_leader = db.execute(sql5, params5).fetchone()

        return render_template(
            "pages/week-page.jinja",
            week=week,
            instruments=instruments,
            week_data=week_data,
            files=files,
            worship_leader=worship_leader,
            week_id=id,
        )


# -----------------------------------------------------------
# New File Upload - handles new file upload form
# -----------------------------------------------------------
@app.post("/newfile/week/<int:id>")
@login_required
def add_file(id):
    # Get the file selected via the form
    file = request.files.get("file", None)
    if not file or file.filename == "":
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
        return redirect(url_for("show_week", id=id))


# -----------------------------------------------------------
# Submit Request Page - shows submit request form
# -----------------------------------------------------------
@app.get("/request/submit")
@login_required
def show_request():
    with connect_db() as db:
        # get weeks the user is on, to display for selecting
        sql = """
            SELECT week_id, week.date FROM roster
            INNER JOIN week
            ON week_id = week.id
            WHERE user_id = ?
        """
        params = (session["user"]["id"],)
        weeks = db.execute(sql, params).fetchall()

        # dont let user submit a request for multiple weeks
        sql2 = """
            SELECT week_id, week.date FROM request
            INNER JOIN week
            ON week_id = week.id
            WHERE user_id = ?
        """
        params2 = (session["user"]["id"],)
        prev_submitted_weeks = db.execute(sql2, params2).fetchall()

    unique_weeks = list(unique_justseen(weeks))

    for week in prev_submitted_weeks:
        if week in unique_weeks:
            unique_weeks.remove(week)

    return render_template("pages/request-submit.jinja", weeks=unique_weeks)


# -----------------------------------------------------------
# Handle Submit Request form
# -----------------------------------------------------------
@app.post("/request/submit")
@login_required
def process_request():
    with connect_db() as db:
        # get and sanitize form data
        week = request.form.get("week")
        message = request.form.get("message", "").strip()

        # check if the user selected a week
        if week:
            # yes, so check if a message was sent
            if message:
                # yes, input request into db with message
                sql = """
                    INSERT INTO request (week_id, user_id, message) VALUES (?, ?, ?)
                """
                params = (week, session["user"]["id"], message)
                db.execute(sql, params)
            else:
                # no, so input request into db without message
                sql2 = """
                    INSERT INTO request (week_id, user_id, message) VALUES (?, ?, ?)
                """
                params2 = (week, session["user"]["id"], "No Message")
                db.execute(sql2, params2)

            # update the availability of the user for this week to be false, so they cant be re-rostered for that week
            sql3 = """
                UPDATE unavailability
                SET available = FALSE
                WHERE user_id = ?
            """
            params3 = (session["user"]["id"],)
            db.execute(sql3, params3)
        # no, so tell them to select a week
        else:
            flash("Please select a week you wish to change", "error")
            return redirect("/request/submit")

        # select date for flash
        sql4 = """
            SELECT date FROM week
            WHERE id=?
        """
        params4 = week
        date = db.execute(sql4, params4).fetchone()
        date = date["date"]

    flash(f"Submitted change request for {date}", "success")
    return redirect("/")


# -----------------------------------------------------------
# Resolve Request Page - shows resolve request form
# -----------------------------------------------------------
@app.get("/request/resolve/<int:u_id>/<int:w_id>")
@admin_required
def show_resolve_request(u_id, w_id):
    with connect_db() as db:
        # select the data about the request
        sql = """
            SELECT week_id, week.date, user_id, user.first_name AS f_name, user.last_name AS l_name, message FROM request
            INNER JOIN week
            ON week_id = week.id
            INNER JOIN user
            ON user_id = user.id
            WHERE user_id = ? AND week_id = ?
        """
        params = (u_id, w_id)
        request = db.execute(sql, params).fetchone()

        # select the data about the instruments the user has on that day
        sql2 = """
            SELECT instrument.name, instrument.id
            FROM roster
            INNER JOIN instrument
            ON instrument_id = instrument.id
            WHERE user_id = ? AND week_id= ?
        """
        params2 = (u_id, w_id)
        instruments = db.execute(sql2, params2).fetchall()

        # select the available users for that day and those instruments
        available_users = []
        for instrument in instruments:
            sql3 = """
                SELECT user.first_name AS f_name, user.last_name AS l_name, user.id AS u_id FROM instrumentUser
                INNER JOIN user
                ON instrumentUser.user_id = user.id
                INNER JOIN unavailability
                ON unavailability.user_id = user.id
                WHERE instrument_id = ? AND unavailability.available = TRUE AND user.id != ?
                ORDER BY user.id ASC
            """
            params3 = (instrument.get("id"), u_id)
            users = db.execute(sql3, params3).fetchall()

            # add the instrument name to the user object
            for user in users:
                user["instrument"] = instrument["name"]
            available_users.extend(users)

        # remove duplicates
        available_users = list(unique_justseen(available_users))
    return render_template(
        "pages/request-resolve.jinja",
        u_id=u_id,
        w_id=w_id,
        request=request,
        available_users=available_users,
        instruments=instruments,
    )


# -----------------------------------------------------------
# Resolve Request - process resolve request form
# -----------------------------------------------------------
@app.post("/request/resolve/<int:u_id>/<int:w_id>")
@admin_required
def process_resolve_request(u_id, w_id):
    with connect_db() as db:
        # select instruments to be updated
        sql = """
            SELECT instrument.name, instrument.id
            FROM roster
            INNER JOIN instrument
            ON instrument_id = instrument.id
            WHERE user_id = ? AND week_id= ?
        """
        params = (u_id, w_id)
        instruments = db.execute(sql, params).fetchall()

        # replace all instruments the user was on that week with the new players
        for instrument in instruments:
            name = instrument.get("name")
            replacement = request.form.get(f"replacement-{name}").strip()
            sql2 = """
                UPDATE roster
                SET user_id = ?
                WHERE week_id = ? and instrument_id = ?
            """
            params2 = (replacement, w_id, instrument.get("id"))
            db.execute(sql2, params2)

        # delete the request from the db, so it doesn't get resolved twice
        sql3 = """
            DELETE FROM request
            WHERE user_id=? AND week_id = ?
        """
        params3 = (u_id, w_id)
        db.execute(sql3, params3)
    return redirect("/")


# -------------------------------------------------------------------
# List of weeks to be made Page - Shows weeks to be added to roster
# -------------------------------------------------------------------
@app.get("/roster/create")
@admin_required
def show_incomplete_weeks():
    with connect_db() as db:
        # get all weeks
        sql = """
            SELECT id, DATE FROM week
        """
        params = ()
        weeks = db.execute(sql, params).fetchall()

        # select all weeks with entries in the roster table
        sql2 = """
            SELECT week_id AS id FROM roster
        """
        params2 = ()
        roster = db.execute(sql2, params2).fetchall()

        # separate the weeks that are already made from the others
        full_weeks = {week["id"] for week in roster}
        useful_weeks = [week for week in weeks if week["id"] not in full_weeks]

        return render_template("pages/weeks-to-complete-list.jinja", weeks=useful_weeks)


# -----------------------------------------------------------
# Add Week details - show form to add users to a week
# -----------------------------------------------------------
@app.get("/week/edit/<int:id>")
@admin_required
def show_edit_week(id):
    with connect_db() as db:
        # select the date of the week being edited
        sql = """
        SELECT date, id FROM week
        WHERE id = ?
        """
        params = (id,)
        week = db.execute(sql, params).fetchone()

        # get instruments
        sql2 = """
            SELECT name, id FROM instrument
        """
        params2 = ()
        # run query
        instruments = db.execute(sql2, params2).fetchall()

        # select all users that are available for that week
        sql3 = """
            SELECT user.first_name AS f_name, user.id AS u_id, instrument.id AS i_id
            FROM instrumentUser
            INNER JOIN user
            ON instrumentUser.user_id = user.id
            INNER JOIN instrument
            ON instrument.id = instrument_id
            INNER JOIN unavailability
            ON unavailability.user_id = user.id
            WHERE unavailability.available = TRUE AND unavailability.week_id = ?
        """
        params3 = (id,)
        users = db.execute(sql3, params3).fetchall()

        return render_template(
            "pages/week-edit.jinja",
            users=users,
            instruments=instruments,
            week=week,
            w_id=id,
        )


# -----------------------------------------------------------
# Submit week - process week fill out form
# -----------------------------------------------------------
@app.post("/week/edit/<int:w_id>")
@admin_required
def process_week(w_id):
    with connect_db() as db:
        # select instruments
        sql = """
            SELECT name, id
            FROM instrument
        """
        params = ()
        instruments = db.execute(sql, params).fetchall()

        # insert the users the admin selected for the week
        for instrument in instruments:
            name = instrument.get("name")
            musician = request.form.get(name).strip()
            sql2 = """
                INSERT INTO roster (user_id, week_id, instrument_id)
                VALUES (?, ?, ?)
            """
            params2 = (musician, w_id, instrument.get("id"))
            db.execute(sql2, params2)

        # select date for flash
        sql3 = """
            SELECT date FROM week WHERE id =?
        """
        params3 = (w_id,)
        week = db.execute(sql3, params3).fetchone()

        flash(f"week - {week['date']} successfuly created", "success")

    return redirect("/roster/create")


# -----------------------------------------------------------
# Create week - process week creation
# -----------------------------------------------------------
@app.get("/new/week")
@admin_required
def create_week():
    with connect_db() as db:
        # select weeks to check if any exist yet
        sql = """
            SELECT date
            FROM week
        """
        params = ()
        weeks = db.execute(sql, params).fetchall()

        # check if there are any existing weeks in the db
        if weeks:
            # yes, so go off them to create next object
            last_week = to_datetime(next(iter(weeks[-1].values())))
            date_object = last_week + timedelta(days=7)
            date = (date_object).strftime("%Y-%m-%d")
        else:
            # no, so calculate next sundays date
            date_object = date.today() + relativedelta(weekday=SU(+1))
            date = (date_object).strftime("%Y-%m-%d")
        # calculate the practice date (Thurdsday before the sunday)
        practice_date = (date_object - timedelta(days=7)).strftime("%Y-%m-%d")

        # enter into weeks, but not anything into roster
        sql2 = """
            INSERT INTO week (date, practice_date)
            VALUES (?,?)
            RETURNING id
        """
        params2 = (date, practice_date)
        week_id = db.execute(sql2, params2).fetchone()
        id = week_id["id"]

        sql3 = """
            SELECT id FROM user
        """
        params3 = ()
        user_ids = db.execute(sql3, params3).fetchall()

        # create records in unavailability table, so users can submit unavailability for that week
        for user in user_ids:
            sql4 = """
                INSERT INTO unavailability (week_id, user_id, available, completed)
                VALUES (?, ?, FALSE, FALSE)
            """
            params4 = (id, user["id"])
            db.execute(sql4, params4)

        flash(f"week - {date} successfuly initialized", "success")

    return redirect("/roster/create")


# -----------------------------------------------------------
# Contact page - Show Contact details
# -----------------------------------------------------------
@app.get("/contact")
def show_contact():
    with connect_db() as db:
        # select admin details
        sql = """
            SELECT first_name, last_name, email FROM user
            WHERE is_admin = TRUE
        """
        params = ()
        admin_details = db.execute(sql, params).fetchall()

    return render_template("pages/contact.jinja", admin_details=admin_details)


# -----------------------------------------------------------
# Legal page - Show Legal details
# -----------------------------------------------------------
@app.get("/legal")
def show_legal():

    return render_template("pages/legal.jinja")


# -----------------------------------------------------------
# delete account route
# -----------------------------------------------------------
@app.get("/delete/account")
def delete_week():
    if session["is_admin"]:
        # cant delete admin account
        flash("Cannot Delete Admin Account", "error")
    else:
        with connect_db() as db:
            # turn on foreign key logic
            sql = "PRAGMA foreign_keys = ON"
            db.execute(sql)

            # delete user
            sql2 = "DELETE FROM user WHERE id = ?"
            params2 = (session["user"]["id"],)
            db.execute(sql2, params2)
            # clear session
            session["logged_in"] = False
            session["user"] = {}
            session["is_admin"] = False

    return redirect("/")

# -----------------------------------------------------------
# delete file route
# -----------------------------------------------------------
@app.get("/delete/file/<int:id>")
def delete_file(id):
    with connect_db() as db:
        sql = """
            SELECT filename FROM file WHERE id = ? 
        """
        params = (id,)
        file = db.execute(sql, params).fetchall()
        # delete file
        file_name = file["filename"]
        # Get the path of the file
        filepath = os.path.join(UPLOAD_FOLDER, file_name)
        # Delete file from disk if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        # delete record from db
        sql2 = """
            DELETE FROM file WHERE id = ?
            RETURNING week_id
        """
        params2 = (id,)
        week_id = db.execute(sql2, params2).fetchone()
        flash(f"{file_name} deleted", "success")  

    return redirect(url_for("show_week", id=week_id['week_id']))


# ===========================================================
# Configure the app
# ===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)
