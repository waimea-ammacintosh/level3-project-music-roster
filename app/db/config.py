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
            role_id        INTEGER, 

            FOREIGN KEY (role_id) REFERENCES role(id)
        )
    """

    SEED_DATA = """
        INSERT INTO user (email, first_name, last_name, pw_hash, role_id)
        VALUES
        ('aaron.macintosh@icloud.com', 'Aaron', 'Macintosh', 'scrypt:32768:8:1$bWFxNHmhbwCRY5lc$7f093fbd397c96d03868f046e2e51cac69ea72598b0c267933982c2b029f7cf8a4f219ca08d37ffe2f6f3bbeeffd5171f253c9291722eb58ff60e01bf262ebec', 0),
        ('bobby@mail.com', 'Bob', 'Looffd', 'scrypt:32768:8:1$bWFxNHmhbwCRY5lc$7f093fbd397c96d03868f046e2e51cac69ea72598b0c267933982c2b029f7cf8a4f219ca08d37ffe2f6f3bbeeffd5171f253c9291722eb58ff60e01bf262ebec', 1)
            
    """

# Add more table classes here...
class WeekTable:

    NAME = "week"

    SCHEMA = """
        CREATE TABLE week (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            DATE NOT NULL,
            practice_date   DATE NOT NULL  
        )
    """

    SEED_DATA = """
        INSERT INTO week (date, practice_date)
        VALUES
        (2026-11-08, 2026-11-05)
            
    """

class FileTable:

    NAME = "file"

    SCHEMA = """
        CREATE TABLE file (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL,
            week_id     INTEGER NOT NULL,

            FOREIGN KEY (week_id) REFERENCES week(id)
        )
    """

    SEED_DATA = """
        INSERT INTO file (filename, week_id)
        VALUES
        ('song.pdf',0)
    """

class RoleTable:

    NAME = "role"

    SCHEMA = """
        CREATE TABLE role (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL

        )
    """

    SEED_DATA = """
        INSERT INTO role (id, name)
        VALUES
        (1, 'admin'),
        (2, 'leader')

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
        ('bass'),
        ('acoustic guitar'),
        ('sing')

    """

class RequestTable:

    NAME = "request"

    SCHEMA = """
        CREATE TABLE request (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      DATE NOT NULL,
            message   TEXT NOT NULL,
            user_id   INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES user(id)  
        )
    """

    SEED_DATA = """
        INSERT INTO request (date, message, user_id)
        VALUES
        (2026-11-08, 'I am most sorry, I am unable to attend this week, as I cannot handle my eyes.', 0)
            
    """

class InstrumentUserTable:

    NAME = "instrumentUser"

    SCHEMA = """
        CREATE TABLE instrumentUser (
            user_id         INTEGER NOT NULL,
            instrument_id   INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (instrument_id) REFERENCES instrument(id)
        )
    """

    SEED_DATA = """
        INSERT INTO instrumentUser (user_id, instrument_id)
        VALUES
        (0, 0)
            
    """

class RosterTable:

    NAME = "roster"

    SCHEMA = """
        CREATE TABLE roster (
            user_id         INTEGER NOT NULL,
            week_id   INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES user(id)
            FOREIGN KEY (week_id) REFERENCES week(id)
        )
    """

    SEED_DATA = """
        INSERT INTO roster (user_id, week_id)
        VALUES
        (0, 0)
            
    """

class UnavailablityTable:

    NAME = "unavailability"

    SCHEMA = """
        CREATE TABLE unavailability (
            user_id   INTEGER NOT NULL,
            week_id   INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES user(id)
            FOREIGN KEY (week_id) REFERENCES week(id)
        )
    """

    SEED_DATA = """
        INSERT INTO unavailability (user_id, week_id)
        VALUES
        (1, 0)
            
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
    RoleTable,
    InstrumentTable,
    UserTable,
    InstrumentUserTable,
    RequestTable,
    RosterTable,
    UnavailablityTable,    
    WeekTable,
    FileTable,
]

