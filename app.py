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


# -- Initialization section --
app = Flask(__name__)


# first let's load environment variables in .env
load_dotenv()


#then store environment variables with new names
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")


# name of database
app.config['MONGO_DBNAME'] = 'studentplanner'
# URI of database
app.config['MONGO_URI'] = f'mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.gwiez.mongodb.net/studentplanner?retryWrites=true&w=majority'
mongo = PyMongo(app)
# -- Routes section --
# INDEX
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', time=datetime.now())
# CONNECT TO DB, ADD DATA

@app.route('/schedule')
def schedule():
    return render_template('schedule.html', time=datetime.now())


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