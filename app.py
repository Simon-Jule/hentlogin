from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
from flask_session import Session
from flask_cors import CORS, cross_origin
#from flask_mysqldb import MySQL#####################
from flaskext.mysql import MySQL
#from pymysql.cursors import DictCursor
import pymysql
#import MySQLdb.cursors ####################
import re

app = Flask(__name__)
# For unit tests
app.config['USERNAME'] = 'test'
app.config['PASSWORD'] = 'test'
app.config['EMAIL'] = 'test@hent.com'
CORS(app)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1234'

######################
#mysql = MySQL(cursorclass=DictCursor)
mysql_ext = MySQL(cursorclass=pymysql.cursors.DictCursor)
######################

# Enter your database connection details below
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'pythonlogin'
app.config['MYSQL_DATABASE_HOST'] = 'db'

# Intialize MySQL#####################
# mysql.init_app(app)
mysql_ext.init_app(app)


def connect_db():
    """Connects to the database."""
    print("connects to the database")
    cnx = mysql_ext.connect()
    cursor = cnx.cursor()

    try:
        cursor.execute("USE {}".format('pythonlogin'))
    # except mysql.connector.Error as err:
    except pymysql.err.InternalError as err:
        code, msg = err.args
        print("Database {} does not exists.".format('pythonlogin'))
        # if err.errno == errorcode.ER_BAD_DB_ERROR:
        # if database is unknown
        if code == 1049:
            print(err)
            # create_db(cursor)
            print("Database {} created successfully.".format('pythonlogin'))
            cnx.database = 'pythonlogin'
        else:
            print(err)
            exit(1)

    return cnx

# creates the database


def create_db(cursor):
    print("creates the database")
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format('pythonlogin'))
    except pymysql.err.InternalError as err:
        print("Failed creating database: {}".format(err))
        exit(1)


def init_db():
    print("initialize the database")
    with app.app_context():
        db = get_db()
        with app.open_resource('schema0.sql', mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()
        with app.open_resource('schema1.sql', mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()
        with app.open_resource('schema2.sql', mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()
        # with app.open_resource('schema3.sql', mode='r') as f:
        #     db.cursor().execute(f.read())
        # db.commit()

# open database connection


def get_db():
    print("open database connection")
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db

# close database connection
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session.modified = True
            session.permanent = True
            # Redirect to home page
            # return redirect(url_for('home'))
            return jsonify("Successfully logged in")
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    # return render_template('index.html', msg=msg)
    return jsonify(msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
@cross_origin(supports_credentials=True)
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    # return redirect(url_for('login'))
    return jsonify("Successfully logged out")

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        conn = conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            msg = 'Invalid email address!'
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            #mysql.connection.commit()####################
            conn.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    # return render_template('register.html', msg=msg)
    return jsonify(msg)

# http://localhost:5000/pythonlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
@cross_origin(supports_credentials=True)
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # return render_template('home.html', username=session['username'])
        return jsonify(session['username'])
    # User is not loggedin redirect to login page
    # return redirect(url_for('login'))
    return jsonify("Redirect to login page")

# http://localhost:5000/pythonlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
@cross_origin(supports_credentials=True)
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        # return render_template('profile.html', account=account)
        return jsonify("success")
    # User is not loggedin redirect to login page
    # return redirect(url_for('login'))
    return jsonify("Redirect to login page")


if __name__ == "__main__":
    init_db()
    app.run()
