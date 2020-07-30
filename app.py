# ---- YOUR APP STARTS HERE ----
# -- Import section --
from datetime import datetime
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
from flask import redirect
import os
from dotenv import load_dotenv
from flask import url_for, session
from authlib.integrations.flask_client import OAuth
from datetime import timedelta
from auth_decorator import login_required
# import quickstart
# import events

# -- Initialization section --
app = Flask(__name__)

# first let's load environment variables in .env
load_dotenv()
# then store environment variables with new names 
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# URI of database
# name of database
app.config['MONGO_DBNAME'] = 'studentplanner'
# URI of database
app.config['MONGO_URI'] = 'mongodb+srv://admin:kyfyt5PyhWkJYqeP@cluster0.gwiez.mongodb.net/studentplanner?retryWrites=true&w=majority'

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

mongo = PyMongo(app)

# -- Routes section --
# INDEX
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', time=datetime.now())
# CONNECT TO DB, ADD DATA

@app.route('/schedule')
@login_required
def schedule():
    name = dict(session)['profile']['name']
    return render_template('schedule.html', name = name, time=datetime.now())


@app.route('/events')
def events():
    
    # return quickstart.main()
    collection = mongo.db.schedule
    events = collection.find({})
    return render_template('show_events.html', events = events, time=datetime.now())

@app.route('/new')
def new():
    return render_template('new_events.html', time=datetime.now())

@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    if request.method == "GET":
        return render_template('new_events.html')
    else:
        user = dict(session)['profile']['email']
        event_name = request.form['event_name']
        date = request.form['date']
        description = request.form['description']
        types = request.form['types']
        #Connect to a database
        events = mongo.db.schedule
        #Add to the database
        events.insert({'event': event_name, "date": date, "description": description, 'types': types, "user":user})
        collection = mongo.db.schedule
        events = collection.find({})
    return render_template('show_events.html', events = events, time=datetime.now())

# @app.route('/logged')
# @login_required
# def hello_world():
#     name = dict(session)['profile']['name']
#     return f'Hello, you are logged in as {name}!'
@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/schedule')


@app.route('/internship_finder', methods=['GET', 'POST'])
@login_required
def internship_finder():
    return render_template('internship_finder.html')
@app.route('/internship_results/<industry>', methods=["GET", "POST"])
def internship_results(industry):
    return render_template('internship_results.html', industry=industry, time=datetime.now())


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')