# import crypt
from . import db
from flask_login import login_required, current_user
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)


@auth.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('Logged out succesfully', category='success')
    # Redirect to the login page or any other desired page
    return redirect(url_for('auth.login'))


@auth.route('/')
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        staffnumber = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(staffnumber=staffnumber).first()

        if user:  # if a user exists with that staffnumber do this
            if check_password_hash(user.password, password):
                flash('Log-in success', category='success')
                session['staffnumber'] = staffnumber
                session['name'] = user.first_name + ' ' + user.last_name
                session['profile_picture'] = user.profile_picture
                if user.admin:
                    session['admin'] = True
                return redirect(url_for('views.home'))
            else:
                flash('The staff-number or password is incorrect', category='error')
        else:
            flash('The staff-number or password is incorrect', category='error')
    return render_template("login.html")


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # pass form inputs to variables
        password1 = request.form.get('password')
        password2 = request.form.get('confirmPassword')
        staffnumber = request.form.get('staffnumber')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hash = ''

        # confirm the email doesn't already exist
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        # confirm the staffnumber doesn't already exist
        elif User.query.filter_by(staffnumber=staffnumber).first():
            flash('That Staff Number is already in use, contact your system administrator if you believe that has been an error', category='error')
        # confirm the passwords match
        elif password1 != password2:
            flash('The passwords must match', category='error')
        # save a new user to the db
        else:
            # hash the password
            hash = generate_password_hash(password1, method='pbkdf2:sha256')
            # create the user object
            new_user = User(password=hash, staffnumber=staffnumber,
                            email=email, first_name=first_name, last_name=last_name, admin=0)
            # add the user to the user db
            db.session.add(new_user)
            # commit that change
            db.session.commit()
            # confirm
            flash('Account creation successful, welcome.', category='success')
            session['staffnumber'] = staffnumber
            session['name'] = first_name + ' ' + last_name
            return redirect(url_for('views.home'))
        # Return the rendered template for POST requests
    return render_template("register.html")


@auth.route('/update_password', methods=['POST'])
def update_password():
    staffnumber = session.get('staffnumber')
    currentpw = request.form.get('currentPassword')
    newpassword = request.form.get('password')
    confirmpw = request.form.get('confirmPassword')
    user = User.query.filter_by(staffnumber=staffnumber).first()

    if user:
        if check_password_hash(user.password, currentpw):  # does the password match?
            if newpassword == confirmpw:  # do the new passwords match?
                # update the password with the new one
                user.password = generate_password_hash(
                    newpassword, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password updated', category='success')
            else:
                flash('The new passwords do not match', category='error')
        else:
            flash('That is not your current password', category='error')
    return redirect(url_for('views.editprofile'))
