# Sprint 2 - Implement Database and Display of Test Data


## Sprint Goals

Implement the database, populated with test data. Create queries that retrieve test data, and display this on web pages as needed. Test and refine the queries and data display, so that it stands as the basis of the next sprint.

### Specific Goals

**Edit these goals as needed**

- Implement the database
- Add test data to the database
- Create the following web pages:
    - Home pages showing...
    - Details page for ...
    - Etc.
- Develop SQL database queries to:
    - Retrieve all ...
    - Retrieve specific ...
    - Etc.


## Testing Table Implementation with test data

I am testing to see wether the tables in my database are working, and can handle test data to get set up to work in the future. To test this, I put a few records in each table, and constructed the database.

Some example Schemas:

![Instrument table Schema](screenshots/Instrument-table-schema.png)

![Instrument-User table Schema](screenshots/Instrument-User-Table-Schema.png)

![Week table Schema](screenshots/Week-table-schema.png)


When I tested the table creation and seeding, there were many bugs. For example, there would often be an extra comma, or a missing value, and the table couldn't be created.
For example:

![Broken File table schema due to a missing comma](screenshots/broken-file-schema-F.K.png)

This led to an error, as a comma was missing after the last column in the table, so the computer couldn't handle the foreign key creation, and caused this error:

![File Table error](screenshots/File-Table-Error.png)

### Changes / Improvements

Because of this, I went through each table, one at a time, and made sure that there were no errors, and that when I recreated the DB, it would create and seed all the tables with no errors. This resulted in each table being able to be created, and handle data, as shown here:

![Successful db creation](screenshots/Successful-db.gif)


## Testing User Data Display

I am testing the display of all the data linked to one user. This is including data such as roles and instruments, which are stored in a separate table. I tested this by running a test query to see how it would handle retrieving data about a specific person. This will be useful later on, for implementing a session.

Table Contents:

![Instrument table content](screenshots/Instrument-table-Content.png) 
![Instrument-User table content](screenshots/InstrumentUser-Table-Content.png) 

![User table content](screenshots/User-Table-Content.png) 
![Role table content](screenshots/Role-Table-Content.png)


Display:

![Display of User Data](screenshots/Displayed-User-Content.png)


### Testing Outcome

As shown in the display, the correct data is displayed for each user, so the system can show the correct information when retrieving data about a user, which could be added to a session.

## Testing Roster display

I am testing the display of the roster. This is to see, with the test data I have put into the system, if it can display the full roster with every person and instrument in the correct week.

Using the following data, The roster returned should be:

![Expected roster table](screenshots/Expected-Roster.png)

Table Contents:

![Roster Table Content](screenshots/Roster-Content.png)
![Instrument table content](screenshots/Instrument-table-Content.png)

![Current User Table Content](screenshots/User-Table-Content-New.png)
![Week Table Content](screenshots/Week-Table-Content.png)


When I ran my algorithm (below), I kept getting an error, and when I fixed the error, it would return two empty lists, which is not what should happen.

![Bad roster SQL and algorithm](screenshots/Roster-Display-Old.png)

### Changes / Improvements

When this would not work, I came up with a new approach that was much simpler, and worked perfectly. This new SQL query makes use of a Cross Join to join the tables, which was something new that I hadn't learnt before, and would then loop through the data on the Jinja template to get the correct display.

![Good roster SQL](screenshots/Roster-Display-New.png)

![Correct roster is shown](screenshots/Roster-display-correct.gif)


## Testing User Register (adding user to user table)

I am testing whether my app can add a user and all its associated data to the db. I tested this by getting my user register form, and inputting a test user. When this happened, everything worked as I intended it, and the correct tables were updated to show the new user.

Original user Table:

![Original User Table](screenshots/User-Table-Content-New.png)

New User Table:

![user Table with new test user implemented](screenshots/User-Table-Test-User.png)

Instrument-User Table:

![New User-Instrument table showing new user](screenshots/Intsrument-User-Table-Content-New.png)


This resulted in the following card being displayed on the user list:

![Test User Card on User list](screenshots/Test-User-Card.png)


## Sprint Review

This sprint has moved my project forward, as it it has helped me to refine and finalize my database, and have a clear understanding of how my database will work, and be implemented into my system. Some things that went well: The implementation of my database with test data, Writing the roster display query and adding new users to the db. These went well, as they worked relatively quickly, and they all helped get my database to be displayed on my web app, and edited from the web app, which moved my project forward. One thing that did not go so well was that I had to refine my db a bit, as there were some things that I hadn't considered before, and I had to make changes that I weren't expecting, which was challenging to do.

