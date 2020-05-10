from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from flask_cors import CORS, cross_origin
#from flask_mysqldb import MySQL#####################
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
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
mysql = MySQL(cursorclass=DictCursor)
######################

# Enter your database connection details below
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'hent'
#app.config['MYSQL_PASSWORD'] = 'password'
#app.config['MYSQL_DB'] = 'pythonlogin'
#########################################
app.config['MYSQL_DATABASE_USER'] = 'hent'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'pythonlogin'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# Intialize MySQL#####################
#mysql = MySQL(app)

mysql.init_app(app)

conn = mysql.connect()

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

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
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

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
@cross_origin(supports_credentials=True)
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
    app.run()
