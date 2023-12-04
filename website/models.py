import pyodbc
from . import db
from flask_login import UserMixin
from sqlalchemy import text


class Adc(db.Model):
    staffnumber = db.Column(db.String(10), primary_key=True)
    firstname = db.Column(db.String(255))
    secondname = db.Column(db.String(255))
    emailaddress = db.Column(db.String(255))
    manager = db.Column(db.String(255))
    initial = db.Column(db.String(10))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roleId = db.Column(db.Integer)
    staffnumber = db.Column(db.String(10), db.ForeignKey('adc.staffnumber'))
    webtoolid = db.Column(db.Integer, db.ForeignKey('webtool.id'))


class Roletype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(50))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffnumber = db.Column(db.String(10))
    webtoolid = db.Column(db.Integer, db.ForeignKey('webtool.id'))
    tasktypeid = db.Column(db.Integer, db.ForeignKey('tasktype.id'))


class Tasktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tasktype = db.Column(db.String(50))


class Webtool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toolname = db.Column(db.String(150))
    ownerstaffnumber = db.Column(
        db.String(10), db.ForeignKey('adc.staffnumber'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    staffnumber = db.Column(db.String(10))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    admin = db.Column(db.Boolean)


# #Define the connection string
# conn_str = (
#     r'DRIVER={SQL Server};'
#     r'SERVER=DESKTOP-DL6VN7O\SQLEXPRESS;'
#     r'DATABASE=WhoDat;'
#     r'Trusted_Connection=yes;'
# )

# # Connect to the SQL Server database
# conn = pyodbc.connect(conn_str)

# # Create a cursor object to interact with the database
# cursor = conn.cursor()

# # Execute a simple query
# cursor.execute('SELECT * FROM users')
# result = cursor.fetchall()

# # Print the result
# print(result)

# # Close the cursor and connection
# cursor.close()
# conn.close()
