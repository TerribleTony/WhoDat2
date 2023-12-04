from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from sqlalchemy import create_engine, MetaData, select, table
import pyodbc
from sqlalchemy.orm import sessionmaker
from website.models import Adc
views = Blueprint('views', __name__)


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


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        print('post request')
        #    Define the connection string for SQL Server
        conn_str = (
            r"mssql+pyodbc://"
            r"DESKTOP-DL6VN7O\SQLEXPRESS/"
            r"WhoDat?driver=ODBC+Driver+17+for+SQL+Server"
        )
        print(conn_str)
        # Create an engine for SQL Server
        sql_server_engine = create_engine(conn_str)

        # Create an engine for SQLite
        sqlite_db_path = "sqlite:///D:/WhoDat2/instance/database.db"
        sqlite_engine = create_engine(sqlite_db_path)

        # Reflect SQL Server tables
        metadata = MetaData()
        metadata.reflect(bind=sql_server_engine)

        # Create SQLite tables
        metadata.create_all(bind=sqlite_engine)

        # Create a session for SQL Server
        Session = sessionmaker(bind=sql_server_engine)
        sql_server_session = Session()

        # Create a session for SQLite
        Session = sessionmaker(bind=sqlite_engine)
        sqlite_session = Session()

        # Copy data from SQL Server to SQLite
        for table in metadata.sorted_tables:
            data = sql_server_session.execute(select([table])).fetchall()
            sqlite_session.execute(table.insert().values(data))

        # Commit changes
        sqlite_session.commit()

        # Close sessions
        sql_server_session.close()
        sqlite_session.close()

        return request(url_for('views.results'))
    return render_template("home.html")


@views.route('/results', methods=['GET', 'POST'])
def results():
    return render_template("results.html")


@views.route('/help')
def help():
    return render_template("help.html")
