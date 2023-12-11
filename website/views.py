from flask import Blueprint, app, redirect, render_template, request, session, url_for, flash, current_app
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from website.models import Adc, Role, Webtool, Task, Roletype, Tasktype, User
from . import db
from werkzeug.utils import secure_filename

import webbrowser
import os

views = Blueprint('views', __name__)


def admin_required(route_function):
    def wrapper(*args, **kwargs):
        if 'admin' in session:
            return route_function(*args, **kwargs)
        else:
            # Redirect to the login page
            flash('you are not an admin', category='error')
            return redirect(url_for('view.home'))

    # Set the name of the wrapper function
    wrapper.__name__ = route_function.__name__
    return wrapper


def login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'staffnumber' in session:
            return route_function(*args, **kwargs)
        else:
            # Redirect to the login page
            flash('you are not logged in.', category='error')
            return redirect(url_for('auth.login'))

    # Set the name of the wrapper function
    wrapper.__name__ = route_function.__name__
    return wrapper


@views.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    admins = User.query.filter_by(admin=True).all()
    users = User.query.all()

    return render_template('admin.html', data1=admins, users=users)


@views.route('/add_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def add_admin():
    if request.method == 'POST':
        selected_user_id = request.form.get('people')
        selected_user = User.query.get(selected_user_id)

        # Check if the selected user exists
        if selected_user:
            # Perform the logic to add admin privileges to the selected user
            selected_user.admin = True
            db.session.commit()
            flash(selected_user.first_name + ' ' + selected_user.last_name +
                  ' is now an admin.', category='success')
        else:
            flash('Selected user not found.', category='error')

        # Redirect to the admin page or any other appropriate page
        return redirect(url_for('views.admin'))

    # Fetch all users from the User table
    users = User.query.all()

    return render_template('add_admin.html', users=users)


@views.route('/remove_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_admin(user_id):
    user = User.query.get(user_id)

    if user:
        if user.staffnumber == '803409':
            flash('on does not simply, remove Tony as admin', category='error')
        else:
            user.admin = False
            db.session.commit()
            flash('Admin privileges removed successfully', category='success')
    else:
        flash('User not found', category='error')

    return redirect(url_for('views.admin'))


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # if request.method == 'POST':
    # return redirect(url_for('views.results'))
    return render_template("home.html")


@views.route('/update_profile', methods=['POST'])
def update_profile():
    staffnumber = session.get('staffnumber')
    user = User.query.filter_by(staffnumber=staffnumber).first()

    # Update user profile based on the submitted form data
    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.email = request.form.get('email')

    # Handle profile picture update if applicable
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture.filename != '':
            # Handle the file upload as needed, save it to the server or cloud storage, update user.profile_picture, etc.
            user.profile_picture = save_profile_picture(profile_picture)
            session['profile_picture'] = user.profile_picture
            # Commit the changes to the database
    db.session.commit()

    flash('Profile updated successfully!', 'success')

    # Redirect back to the editprofile page or wherever you want after the update
    return redirect(url_for('views.editprofile'))


# page load event for edit profile
@views.route('/editprofile', methods=['GET'])
@login_required
def editprofile():
    staffnumber = session.get('staffnumber')
    edit_user = User.query.filter_by(staffnumber=staffnumber).first()

    return render_template("editprofile.html", edit_user=edit_user)


@views.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    if request.method == 'POST':
        staff_input = request.form.get('staffInput')
        if staff_input and staff_input.isdigit() and len(staff_input) == 6:
            staffnumber_param = request.form.get('staffInput')

            wtadc_alias = aliased(Adc, name='wtadc_alias')
            taskadc_alias = aliased(Adc, name='taskadc_alias')
            roleadc_alias = aliased(Adc, name='roleadc_alias')

            data2 = db.session.query(
                taskadc_alias.firstname + ' ' + taskadc_alias.secondname,
                Task.staffnumber,
                Tasktype.tasktype,
                Webtool.toolname,
                wtadc_alias.firstname + ' ' + wtadc_alias.secondname
            ).join(Tasktype, Task.tasktypeid == Tasktype.id
                   ).join(taskadc_alias, Task.staffnumber == taskadc_alias.staffnumber
                          ).join(wtadc_alias, Webtool.ownerstaffnumber == wtadc_alias.staffnumber
                                 ).join(Webtool, Task.webtoolid == Webtool.id
                                        ).filter(Task.staffnumber == staffnumber_param).all()

            data1 = db.session.query(
                roleadc_alias.firstname + ' ' + roleadc_alias.secondname,
                Role.staffnumber,
                Roletype.rolename,
                Webtool.toolname,
                wtadc_alias.firstname + ' ' + wtadc_alias.secondname
            ).join(Roletype, Role.roleId == Roletype.id
                   ).join(roleadc_alias, Role.staffnumber == roleadc_alias.staffnumber
                          ).join(Webtool, Role.webtoolid == Webtool.id
                                 ).join(wtadc_alias, Webtool.ownerstaffnumber == wtadc_alias.staffnumber
                                        ).filter(Role.staffnumber == staffnumber_param).all()
            if not results:
                return render_template('no_results_template.html')
            return render_template('results.html', data2=data2, data1=data1)
        else:
            staffname_param = request.form.get('staffInput')

            wtadc_alias = aliased(Adc, name='wtadc_alias')
            taskadc_alias = aliased(Adc, name='taskadc_alias')
            roleadc_alias = aliased(Adc, name='roleadc_alias')

            data2 = db.session.query(
                taskadc_alias.firstname + ' ' + taskadc_alias.secondname,
                Task.staffnumber,
                Tasktype.tasktype,
                Webtool.toolname,
                wtadc_alias.firstname + ' ' + wtadc_alias.secondname
            ).join(Tasktype, Task.tasktypeid == Tasktype.id
                   ).join(taskadc_alias, Task.staffnumber == taskadc_alias.staffnumber
                          ).join(wtadc_alias, Webtool.ownerstaffnumber == wtadc_alias.staffnumber
                                 ).join(Webtool, Task.webtoolid == Webtool.id
                                        ).filter(or_(
                                            taskadc_alias.firstname.like(
                                                f"%{staffname_param}%"),
                                            taskadc_alias.secondname.like(
                                                f"%{staffname_param}%")
                                        )).all()

            data1 = db.session.query(
                roleadc_alias.firstname + ' ' + roleadc_alias.secondname,
                Role.staffnumber,
                Roletype.rolename,
                Webtool.toolname,
                wtadc_alias.firstname + ' ' + wtadc_alias.secondname
            ).join(Roletype, Role.roleId == Roletype.id
                   ).join(roleadc_alias, Role.staffnumber == roleadc_alias.staffnumber
                          ).join(Webtool, Role.webtoolid == Webtool.id
                                 ).join(wtadc_alias, Webtool.ownerstaffnumber == wtadc_alias.staffnumber
                                        ).filter(or_(
                                            roleadc_alias.firstname.like(
                                                f"%{staffname_param}%"),
                                            roleadc_alias.secondname.like(
                                                f"%{staffname_param}%")
                                        )).all()
            if not results:
                return render_template('no_results_template.html')
            return render_template('results.html', data2=data2, data1=data1)
    else:
        return render_template('results.html')

# open email to demo what email would be sent.


def open_email_template(subject, body):
    mailto_url = f"mailto:?subject={subject}&body={body}"
    webbrowser.open(mailto_url)


def save_profile_picture(file):
    if file:
        # Get the current app's root path
        app_root = current_app.root_path

        # Specify the folder where you want to save profile pictures
        upload_folder = os.path.join(app_root, 'static', 'uploads')

        # Ensure the folder exists; create it if not
        os.makedirs(upload_folder, exist_ok=True)

        # Use secure_filename to generate a secure version of the filename
        filename = secure_filename(file.filename)

        # Save the file to the designated folder
        file.save(os.path.join(upload_folder, filename))

        # Return the filename or the full path if needed
        return filename

    # Return None if no file is provided
    return None


@views.route('/help')
def help():
    return render_template("help.html")


@views.route('/test')
def test():
    return render_template("test.html")
