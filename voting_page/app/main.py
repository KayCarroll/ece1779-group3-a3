
from flask import render_template, url_for, request, g
from app import webapp, memcache
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app import dynamodb, dynamodb_client, s3_client, lambda_client
from app.config_variables import VOTING_INFO_TABLE, VOTER_INFO_TABLE, salt, S3_bucket_name, LAMBDA_UPDATE_VOTE_FUNCTION
import os
import glob

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup
import secrets
import hashlib


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

def password_hashing(password):
    dataBase_password = password + salt
    hashed_password = hashlib.md5(dataBase_password.encode())
    return hashed_password.hexdigest()

def verify_voter(voter_name, password):
    if not voter_name:
        return False
    table = dynamodb.Table(VOTER_INFO_TABLE)
    response = table.get_item( Key={ 'voter_name': voter_name } )
    if 'Item' in response:
        voter_info = response['Item']
        hashed_pass = password_hashing(password)
        if voter_info['password'] == hashed_pass:
            return True, voter_info
        else:
            return False, None
    else:
        return False, None

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
    else:
        return render_template("message.html", user_message = "There is no active vote.", return_addr = "vote")

    return render_template("vote.html", candidate_list = candidates)

@webapp.route('/vote', methods=['POST'])
def handle_vote():
    user_name = request.form["voter_name"]
    password = request.form["voter_passwd"]
    (voter_verified, voter_info) = verify_voter(user_name, password)
    if voter_verified:
        candidate_choice = request.form.get('candidate_options')
        if not candidate_choice:
            return render_template("message.html", user_message = "No Candidate Selected.", return_addr = "vote")
        s3_path = voter_info["voter_info"]
        already_voted = voter_info["already_voted"]
        try:
            s3_response = s3_client.get_object(
                Bucket=S3_bucket_name,
                Key=s3_path
            )
        except Exception as e:
            print(e)
            return render_template("message.html", user_message = e, return_addr = "vote")
        s3_object_body = s3_response.get('Body')
        content_str = s3_object_body.read().decode()
        info_list = content_str.split("\n")
        result_list = ["First Name: " + info_list[0],
                       "Last Name: " + info_list[1],
                       "Birthday: " + info_list[2],
                       "Street Address: " + info_list[3],
                       "Unit Number: " + info_list[4],
                       "City: " + info_list[5],
                       "Province: " + info_list[6],
                       "Postal Code: " + info_list[7]]
        if already_voted == "True":
            return render_template("message.html", list_title = "Your information: ", input_list=result_list, user_message="You have already voted! The vote is not collected!", return_addr = "vote")
        else:
            response = dynamodb_client.update_item(TableName=VOTER_INFO_TABLE,
                                           Key={'voter_name': {'S': user_name}},
                                           ExpressionAttributeValues={':av': {'S': "True"}},
                                           UpdateExpression=f'SET already_voted = :av')
        test_event = {"body": {
            "candidate": candidate_choice
            }
        }
        response = lambda_client.invoke(
            FunctionName=LAMBDA_UPDATE_VOTE_FUNCTION,
            Payload=json.dumps(test_event),
        )
        response_payload = json.loads(response['Payload'].read())
        return render_template("message.html", list_title = "Your information: ", input_list=result_list, user_message="Candidate Selected: " + candidate_choice, return_addr = "vote")
    else:
        return render_template("message.html", user_message = "Your credential did not match our database.", return_addr = "vote")



@webapp.route('/create_voter', methods=['GET'])
def create_voter():
    username = request.args.get('username')
    password = request.args.get('password')
    hashed_passwd = password_hashing(password)
    print("Hashed Password: " + hashed_passwd)
    table = dynamodb.Table(VOTER_INFO_TABLE)
    response = table.put_item(
        Item={
            'voter_name': username,
            'password': hashed_passwd   ,
            "voter_info": f"voterinfo/{username}.txt"
        }
    )
    try:
        response = s3_client.upload_file(Filename="amy.txt", Bucket=S3_bucket_name, Key=f"voterinfo/{username}.txt")
    except Exception as e:
        print(e)
        return render_template("message.html", user_message = "S3 Upload failed.", return_addr = "vote")
    return render_template("message.html", user_message = "Candidate created: " + username + " password: " + password, return_addr = "vote")

@webapp.route('/verify_voter', methods=['GET'])
def verify_voter_handle():
    username = request.args.get('username')
    password = request.args.get('password')
    result = verify_voter(username, password)
    return render_template("message.html", user_message = "Voter verified: " + str(result[0]), return_addr = "vote")
