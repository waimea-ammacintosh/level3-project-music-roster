#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

class UserTable:

    NAME = "user"

    SCHEMA = """
        CREATE TABLE user (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            email          TEXT NOT NULL,
            first_name     TEXT NOT NULL,
            last_name      TEXT NOT NULL,
            pw_hash        TEXT NOT NULL,
            instrument_id  INTEGER NOT NULL,
            role_id        INTEGER 
        )
    """

    SEED_DATA = """
        INSERT INTO user (email, first_name, last_name, pw_hash, instrument_id, role_id)
        VALUES
            
    """

# Add more table classes here...
class WeekTable:

    NAME = "week"

    SCHEMA = """
        CREATE TABLE week (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            DATE NOT NULL,
            practice_date   DATE NOT NULL,
            file_id         BIGINT
,  
        )
    """

    SEED_DATA = """
        INSERT INTO week (date, practice_date, file_id)
        VALUES
            
    """

class FileTable:

    NAME = "file"

    SCHEMA = """
        CREATE TABLE file (
            id          BIGINT PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL
        )
    """

    SEED_DATA = """
        INSERT INTO file (filename)
        VALUES
    """

class RoleTable:

    NAME = "role"

    SCHEMA = """
        CREATE TABLE role (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL

        )
    """

    SEED_DATA = """
        INSERT INTO role (name)
        VALUES

    """

class InstrumentTable:

    NAME = "instrument"

    SCHEMA = """
        CREATE TABLE instrument (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL

        )
    """

    SEED_DATA = """
        INSERT INTO instrument (name)
        VALUES

    """

class RequestTable:

    NAME = "request"

    SCHEMA = """
        CREATE TABLE request (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      DATE NOT NULL,
            message   DATE NOT NULL,
            user_id   INTEGER NOT NULL
,  
        )
    """

    SEED_DATA = """
        INSERT INTO request (date, message, user_id)
        VALUES
            
    """

#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    UserTable,
    WeekTable,
    FileTable,
    RoleTable,
    InstrumentTable,
    RequestTable,
    

    # Add more tables here...
]

