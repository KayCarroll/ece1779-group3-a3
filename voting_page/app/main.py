
from flask import render_template, url_for, request, g
from app import webapp, memcache
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app import dynamodb, dynamodb_client
from app.config_variables import db_config, VOTING_INFO_TABLE, VOTER_INFO_TABLE
import os
import glob

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_current_vote():
    response = dynamodb_client.scan(TableName=VOTING_INFO_TABLE, Select='ALL_ATTRIBUTES',
                                    FilterExpression='currently_active = :activeval',
                                    ExpressionAttributeValues={':activeval': {'S': 'True'}})

    current_vote = None
    if len(response['Items']) == 1:
        current_vote = response['Items'][0]
    elif response['Items']:
        print(f'There is more than one currently active vote!')
    else:
        print('There are no currently active votes.')

    return current_vote

def verify_voter(voter_name, password):
    if not voter_name:
        return False
    table = dynamodb.Table(VOTER_INFO_TABLE)
    response = table.get_item( Key={ 'voter_name': voter_name } )
    if 'Item' in response:
        voter_info = response['Item']
        if voter_info['password'] == password:
            return True
        else:
            return False
    else:
        return False
    # response = dynamodb_client.scan(TableName=VOTING_INFO_TABLE, Select='ALL_ATTRIBUTES',
    #                                 FilterExpression='currently_active = :activeval',
    #                                 ExpressionAttributeValues={':activeval': {'S': 'True'}})

@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/navbar')
def global_navbar():
    return render_template("navbar.html")

@webapp.route('/vote')
def vote_page():
    current_vote = get_current_vote()
    disable = False
    candidates = []
    if current_vote:
        vote_name = current_vote['election_name']['S']
        start_time = current_vote['start_time']['S']
        end_time = current_vote['end_time']['S']
        candidates = list(json.loads(current_vote['candidates']['S']).values())
        print(candidates)
    else:
        print("No active vote")
        disable = True

    return render_template("vote.html", candidate_list = candidates)

@webapp.route('/vote', methods=['POST'])
def handle_vote():
    user_name = request.form["voter_name"]
    password = request.form["voter_passwd"]
    if verify_voter(user_name, password):
        candidate_choice = request.form.get('candidate_options')
        if not candidate_choice:
            return render_template("message.html", user_message = "No Candidate Selected.", return_addr = "vote")
        return render_template("message.html", user_message = "Candidate selected: " + candidate_choice, return_addr = "vote")
    else:
        return render_template("message.html", user_message = "Your credential did not match our database.", return_addr = "vote")



@webapp.route('/create_voter', methods=['GET'])
def create_voter():
    username = request.args.get('username')
    password = request.args.get('password')
    table = dynamodb.Table(VOTER_INFO_TABLE)
    response = table.put_item(
        Item={
            'voter_name': username,
            'password': password,
            "voter_info": f"voterinfo/{username}.txt"
        }
    )
    return render_template("message.html", user_message = "Candidate created: " + username + " password: " + password, return_addr = "vote")

@webapp.route('/verify_voter', methods=['GET'])
def verify_voter_handle():
    username = request.args.get('username')
    password = request.args.get('password')
    result = verify_voter(username, password)
    return render_template("message.html", user_message = "Voter verified: " + str(result), return_addr = "vote")
