#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory
from markupsafe import escape
import pymongo
import datetime
from bson.objectid import ObjectId
import os
import subprocess
from sudoku_cv_picprocess import predict_board
import solver
# instantiate the app
app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'uploads'


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

    return render_template('input.html') #, solved  # render the create template

@app.route('/uploading', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        img = request.files['sudoku_pic']
        img.save(img.filename)
 
        return redirect(url_for('solve', img = img.filename))

 # tell the browser to make a request for the /read route

@app.route('/solve/<img>')
def solve(img):
    """
    Route for GET requests to the edit page.
    Displays a form users can fill out to edit an existing record.
    """
    read = predict_board(img, 'PytorchModel_AddFonts_space_duplicate.pt')
    ans = []
    solver.solve(read, ans)

    return render_template('grid.html', read = ans[0]) # render the edit template



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
