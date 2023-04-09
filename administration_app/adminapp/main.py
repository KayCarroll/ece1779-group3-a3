from flask import render_template, url_for, request, g
from adminapp import app, dynamodb_client


@app.route('/')
def main():
    return render_template('main.html')

@app.route('/home')
def home():
    return render_template('main.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/current')
def current():
    return render_template('current.html')

@app.route('/past')
def past():
    return render_template('past.html')
