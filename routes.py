from flask import Flask, render_template, flash, redirect, request, session, g
import flask_sqlalchemy, os
from sqlite3 import dbapi2 as sqlite3
from flask_sqlalchemy import SQLAlchemy
import socket
from socket import gethostbyname
from passlib.hash import sha256_crypt

app = Flask(__name__)
db = SQLAlchemy(app)
session = {'logged_in': False, 'user_id': 0}

#Db methods taken from flaskr tutorial on github
#________________________________________________________________________________________
# Load default config and override config from an environment variable

#CONFIG IS TEMP, WILL CHANGE FOR SECURITY
app.config.update(dict(
    DATABASE=('blogSite.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect('blogSite.db')
	rv.row_factory = sqlite3.Row
	return rv

def init_db():
	with app.open_resource('schema.sql', mode='r') as f:
		db = get_db()
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')
	

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#Db methods end
#________________________________________________________________________________________
session = {'authenticated': False, 'Admin': False}
@app.route('/')
def start():
	session['authenticated'] = False
	session['Admin'] = False
	return redirect('/home')
	
@app.route('/home')
def home():
	db = get_db()
	cur = db.execute('select title, description, post_body, date, author, post_id from posts')
	posts = cur.fetchall()
	isAdmin = session['Admin']
	return render_template('layout.html', posts = posts, isAdmin = isAdmin)
	
@app.route('/createPost', methods=['GET', 'POST'])
def createPost():
	#Get posts to display
	if(request.method == 'POST'):
		title = request.form['Title']
		body = request.form['body']
		#Put in database
		addPost(title, body)
		
	db = get_db()
	cur = db.execute('select title, description, post_body, date, author, post_id from posts')
	posts = cur.fetchall()
	return render_template('createPost.html', posts = posts, isAdmin = session['Admin'])
	
@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
	#Get posts to display
	if(request.method == 'POST'):
		username = request.form['username']
		password = request.form['password']
		#Put in database
		addAccount(username, sha256_crypt.encrypt(password))
		
	db = get_db()
	cur = db.execute('select title, description, post_body, date, author, post_id from posts')
	posts = cur.fetchall()
	return render_template('createAccount.html', posts = posts, isAdmin = session['Admin'] )

@app.route('/login', methods=['GET', 'POST'])	
def login():
	if(request.method == 'POST'):
		username = request.form['username']
		password = request.form['password']
		
		#Get expected password
		db = get_db()
		cur = db.execute('select password from users where username = ?', (username,))
		expected_password = (cur.fetchone())[0]
		
		if(sha256_crypt.verify(password,expected_password) == True):
			flash('Logged In')
			session['authenticated'] = True			
			if(username == "admin"):
				session['Admin'] = True
			return redirect('/home')
		else:
			flash('Login Unsuccessful')
			return redirect('/login')
			
	isAdmin = session['authenticated']
	db = get_db()
	cur = db.execute('select title, description, post_body, date, author, post_id from posts')
	posts = cur.fetchall()
	return render_template('login.html', posts = posts, isAdmin = isAdmin )
	
#Routing ends 
#Helper methods begin
#_______________________________________________________________________________________


def addPost(title, body):
	db = get_db()
	db.execute('insert into posts (title, post_body, description, author) values (?,?,?,?)',
	[title, body, "Test Description", "System User"])
	db.commit()	

def addAccount(username, password):
	db = get_db()
	db.execute('insert into users (username, password) values (?,?)',
	[username, password])
	db.commit()	
	
#Helper methods end
#_______________________________________________________________________________________	

if __name__ == '__main__':
	with app.app_context():
		
		if('liveconsole' not in socket.gethostname()):
			init_db()
			app.run(debug=True)