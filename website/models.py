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
    notified = db.Column(db.Boolean)


class Roletype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(50))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffnumber = db.Column(db.String(10))
    webtoolid = db.Column(db.Integer, db.ForeignKey('webtool.id'))
    tasktypeid = db.Column(db.Integer, db.ForeignKey('tasktype.id'))
    notified = db.Column(db.Boolean)


class Tasktype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tasktype = db.Column(db.String(50))


class Webtool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toolname = db.Column(db.String(150))
    ownerstaffnumber = db.Column(
        db.String(10), db.ForeignKey('adc.staffnumber'))
    status = db.Column(db.Boolean)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    staffnumber = db.Column(db.String(10))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    admin = db.Column(db.Boolean)
    profile_picture = db.Column(db.String(120), default='default.jpg')

# how to update tables manually
# type 'sqlite3 instance/database.db' into the terminal

# type sql directly into the terminal for eg
# INSERT INTO users (username, email) VALUES ('john_doe', 'john@example.com');
