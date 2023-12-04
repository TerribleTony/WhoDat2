# import crypt
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

# Initialize Bcrypt
# bcrypt = crypt()
# # Function to hash a password using Bcrypt


# def hash_password(password):
#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#     return hashed_password

# Function to hash a password
# def hash_password(password):
#     sha256 = hashlib.sha256()
#     password_bytes = password.encode('utf-8')
#     sha256.update(password_bytes)
#     hashed_password = sha256.hexdigest()
#     return hashed_password

# Route for the logout functionality


@auth.route('/logout')
def logout():
    # Clear the session
    session.clear()

    # Redirect to the login page or any other desired page
    return redirect(url_for('auth.login'))


@auth.route('/')
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        staffnumber = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(staffnumber=staffnumber).first()
        print(generate_password_hash(password, method='pbkdf2:sha256'))
        print(staffnumber)
        if user:
            if check_password_hash(user.password, password):
                flash('Log-in success', category='success')
                session['staffnumber'] = staffnumber
                return redirect(url_for('views.home'))
            else:
                flash('The staff-number or password is incorrect', category='error')
        else:
            flash('The staff-number or password is incorrect', category='error')
    return render_template("login.html")


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print('recognised POST method')
        # pass form inputs to variables
        password1 = request.form.get('password')
        password2 = request.form.get('confirmPassword')
        staffnumber = request.form.get('staffnumber')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hash = ''
        print(password1 + staffnumber + email + first_name + last_name)

        # confirm the email doesn't already exist
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
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
            flash('Account creation successful', category='success')
            return redirect(url_for('views.home'))
        # Return the rendered template for POST requests
    return render_template("register.html")
