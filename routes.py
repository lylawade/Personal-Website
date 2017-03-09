from flask import Flask, render_template, flash, redirect, request, session, g
import flask_sqlalchemy, os
from sqlite3 import dbapi2 as sqlite3
from flask_sqlalchemy import SQLAlchemy
import socket
from socket import gethostbyname

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
@app.route('/')
def home():
	db = get_db()
	addDummyPosts();
	cur = db.execute('select title, description, post_body, date, author, post_id from posts')
	posts = cur.fetchall()
	return render_template('layout.html', posts = posts)

@app.route('/createPost', methods=['GET', 'POST'])
def createPost():
	#Get posts to display
	db = get_db()
	cur = db.execute('select title, description, post_body, date, author, post_id from posts')
	posts = cur.fetchall()
	return render_template('createPost.html', posts = posts)
	
@app.route('/login', methods=['GET', 'POST'])	
def login():
	#TO DO
	#Only display "Create Post" page when logged in
	#As admin/Lyla
	return redirect('/')
	
#Routing ends 
#_______________________________________________________________________________________

def addDummyPosts():
	i = 0
	db = get_db()
	
	while(i<3):
		db.execute('insert into posts (title, post_body, description, author) values (?,?,?,?)',
		["Title " + str(i), "Fashion fashion and mauris neque quam, fermentum ut nisl vitae, convallis maximus nisl. Sed mattis nunc id lorem euismod placerat. Vivamus porttitor magna enim, ac accumsan tortor cursus at.", "Description " + str(i), "System User"])
		db.commit()	
		i+=1

if __name__ == '__main__':
	#Uncomment below when deployed on server
	#If uncommented, everytime route.py is run
	#database is reinitialized
	with app.app_context():
		
		if('liveconsole' not in socket.gethostname()):
			init_db()
			app.run(debug=True)