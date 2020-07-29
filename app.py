# ---- YOUR APP STARTS HERE ----
# -- Import section --
from __future__ import print_function
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
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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
# def schedule():
#     name = dict(session)['profile']['name']
#     return render_template('schedule.html', name = name, time=datetime.now())
# If modifying these scopes, delete the file token.pickle.

def main():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


@app.route('/events')
def events():
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
        event_name = request.form['event_name']
        date = request.form['date']
        description = request.form['description']
        types = request.form['types']
        #Connect to a database
        events = mongo.db.schedule
        #Add to the database
        events.insert({'event': event_name, "date": date, "description": description, 'types': types})
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
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/schedule')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')