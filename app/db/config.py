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
            is_admin       BOOL DEFAULT FALSE
        )
    """

    SEED_DATA = """
        INSERT INTO user (email, first_name, last_name, pw_hash, is_admin)
        VALUES
        ('aaron.macintosh@icloud.com', 'Aaron', 'Macintosh', 'scrypt:32768:8:1$tfKjizzt87rOrItD$7c0b7b8269434224f29ec37e0b8de4dbee1f54fbd0d5a48225845a9706362702e7ffaff2fc9aa6d452a18a00e618e23114b164403350f68da2781dd9c4a0efed', FALSE),
        ('bobby@mail.com', 'Bob', 'Looffd', 'scrypt:32768:8:1$tfKjizzt87rOrItD$7c0b7b8269434224f29ec37e0b8de4dbee1f54fbd0d5a48225845a9706362702e7ffaff2fc9aa6d452a18a00e618e23114b164403350f68da2781dd9c4a0efed', FALSE),
        ('jimmy@yahoo.com', 'Jimmy', 'Carlsen', 'scrypt:32768:8:1$bWFxNHmhbwCRY5lc$7f093fbd397c96d03868f046e2e51cac69ea72598b0c267933982c2b029f7cf8a4f219ca08d37ffe2f6f3bbeeffd5171f253c9291722eb58ff60e01bf262ebec', TRUE)   
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
        ('2026-11-08', '2026-11-05'),
        ('2026-11-15', '2026-11-12'),
        ('2026-11-22', '2026-11-19'),
        ('2026-11-29', '2026-11-26')


            
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
        ('pdftris.pdf', 1)
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
        ('Worship Lead'),
        ('bass'),
        ('acoustic guitar'),
        ('sing')
        

    """

class RequestTable:

    NAME = "request"

    SCHEMA = """
        CREATE TABLE request (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            week_id    INTEGER NOT NULL,
            message    TEXT NOT NULL,
            user_id    INTEGER NOT NULL,     

            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (week_id) REFERENCES week(id)  
        )
    """

    SEED_DATA = """
        INSERT INTO request (week_id, message, user_id)
        VALUES
        (1, 'I am most sorry, I am unable to attend this week, as I cannot handle my eyes.', 1)
            
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
        (1, 1),
        (1, 2),
        (1, 4),
        (2, 3)
            
    """

class RosterTable:

    NAME = "roster"

    SCHEMA = """
        CREATE TABLE roster (
            user_id         INTEGER NOT NULL,
            week_id         INTEGER NOT NULL,
            instrument_id   INTEGER NOT NULL,

            FOREIGN KEY (user_id) REFERENCES user(id)
            FOREIGN KEY (week_id) REFERENCES week(id)
            FOREIGN KEY (instrument_id) REFERENCES instrument(id)
        )
    """

    SEED_DATA = """
        INSERT INTO roster (user_id, week_id, instrument_id)
        VALUES
        (1, 1, 1),
        (2, 1, 3),
        (1, 2, 2),
        (1, 2, 1)
            
    """

class UnavailabilityTable:

    NAME = "unavailability"

    SCHEMA = """
        CREATE TABLE unavailability (
            user_id     INTEGER NOT NULL,
            week_id     INTEGER NOT NULL,
            available   BOOLEAN NOT NULL,
            completed   BOOLEAN NOT NULL DEFAULT FALSE,

            FOREIGN KEY (user_id) REFERENCES user(id)
            FOREIGN KEY (week_id) REFERENCES week(id)
        )
    """

    SEED_DATA = """
        INSERT INTO unavailability (user_id, week_id, available, completed)
        VALUES
        (1, 1, TRUE, TRUE),
        (1, 2, TRUE, TRUE),
        (1, 3, FALSE, FALSE),
        (1, 4, FALSE, FALSE),
        (2, 1, TRUE, TRUE),
        (2, 2, FALSE, TRUE),
        (2, 3, FALSE, FALSE),
        (2, 4, FALSE, FALSE)
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
    InstrumentTable,
    UserTable,
    InstrumentUserTable,
    RequestTable,
    RosterTable,
    UnavailabilityTable,    
    WeekTable,
    FileTable,
]

