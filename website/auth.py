# import crypt
from password_strength import PasswordPolicy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Regexp
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
    form = RegistrationForm()
    print(form.errors)
    if form.validate_on_submit():

        # pass form inputs to variables
        password1 = form.password.data
        password2 = form.confirm_password.data
        staffnumber = form.staffnumber.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
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
            hash = generate_password_hash(
                password1, method='pbkdf2:sha256')
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
    print(form.errors)
    return render_template("register.html", form=form)


class RegistrationForm(FlaskForm):

    staffnumber = StringField('Staff Number', validators=[
        Length(min=6, max=6, message='Staff number must contain exactly 6 digits.'),
        Regexp('^\d*$', message='Staff number must contain only digits.')
    ])

    first_name = StringField('First Name', validators=[DataRequired()])

    last_name = StringField('Last Name', validators=[DataRequired()])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[
        DataRequired(),
        Regexp(
            '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message='Password must meet the specified requirements.')

    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])

    def validate_password(self, password):
        policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
            nonletters=1,
        )

        errors = [str(err) for err in policy.test(password.data)]
        if errors:
            raise ValidationError(" ".join(errors))

        # Check if the password is in the blacklist
        common_passwords = ['password', '123456', 'qwerty', 'letmein', 'admin']
        if password.data.lower() in common_passwords:
            raise ValidationError('Please choose a more secure password.')

    submit = SubmitField('Register')


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
