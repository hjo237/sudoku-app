#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response
from markupsafe import escape
import pymongo
import datetime
from bson.objectid import ObjectId
import os
import subprocess
import solver
from sudoku_cv import *

# instantiate the app
app = Flask(__name__)

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
import credentials
config = credentials.get()

# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode

# make one persistent connection to the database
connection = pymongo.MongoClient(config['MONGO_HOST'], 27017, 
                                username=config['MONGO_USER'],
                                password=config['MONGO_PASSWORD'],
                                authSource=config['MONGO_DBNAME'])
db = connection[config['MONGO_DBNAME']] # store a reference to the database

# set up the routes

@app.route('/')
def home():
    """
    Route for the home page
    """
    return render_template('homepage.html')


@app.route('/upload')
def upload():
    """
    Route for GET requests to the create page.
    Displays a form users can fill out to create a new review.
    """
    image = request.files.get("myImage")

    sudoku = predict_board(image) 

    solved = solve(sudoku)

    return render_template('input.html'), solved  # render the create template


@app.route('/edit/<mongoid>')
def edit_review(mongoid):
    """
    Route for GET requests to the edit page.
    Displays a form users can fill out to edit an existing record.
    """
    doc = db.reviews.find_one({"_id": ObjectId(mongoid)})
    return render_template('edit_review.html', mongoid=mongoid, doc=doc) # render the edit template


@app.route('/edit/<mongoid>', methods=['POST'])
def edit_post(mongoid):
    """
    Route for POST requests to the edit page.
    Accepts the form submission data for the specified review and updates the review in the database.
    """
    name = request.form['fname']
    review = request.form['fmessage']
    rating = request.form['frating']

    doc = {
        # "_id": ObjectId(mongoid), 
        "name": name, 
        "review": review, 
        "rating": rating,
        "created_at": datetime.datetime.utcnow()
    }

    db.reviews.update_one(
        {"_id": ObjectId(mongoid)}, # match criteria
        { "$set": doc }
    )

    return redirect(url_for('read_review')) # tell the browser to make a request for the /read route



@app.route('/delete/<mongoid>')
def delete_review(mongoid):
    """
    Route for GET requests to the delete page.
    Deletes the specified record from the database, and then redirects the browser to the read page.
    """
    db.reviews.delete_one({"_id": ObjectId(mongoid)})
    return redirect(url_for('read_review')) # tell the web browser to make a request for the /read route.


@app.route('/menu')
def menu():
    """
    Route for GET requests to the read page.
    Displays menu for the user to give information.
    """
    return render_template('menu.html')


@app.route('/hours')
def hours():
    """
    Route for GET requests to the read page.
    Displays opening hours for the user to give information.
    """
    return render_template('hours.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    GitHub can be configured such that each time a push is made to a repository, GitHub will make a request to a particular web URL... this is called a webhook.
    This function is set up such that if the /webhook route is requested, Python will execute a git pull command from the command line to update this app's codebase.
    You will need to configure your own repository to have a webhook that requests this route in GitHub's settings.
    Note that this webhook does do any verification that the request is coming from GitHub... this should be added in a production environment.
    """
    # run a git pull command
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    pull_output = process.communicate()[0]
    # pull_output = str(pull_output).strip() # remove whitespace
    process = subprocess.Popen(["chmod", "a+x", "flask.cgi"], stdout=subprocess.PIPE)
    chmod_output = process.communicate()[0]
    # send a success response
    response = make_response('output: {}'.format(pull_output), 200)
    response.mimetype = "text/plain"
    return response

@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e) # render the edit template


if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)
