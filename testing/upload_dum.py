# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 19:09:53 2023

@author: Sam
"""

import requests 
import random

from flask import render_template, url_for, request, g

from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
import os
import glob

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup
import secrets

import boto3
import hashlib
S3_bucket_name = "ece1779-a3-test1"
ACCESS_KEY = "AKIARYPZNG6KRLLMQZ3X"
SECRET_KEY = "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"
VOTING_INFO_TABLE = 'voting_info'
VOTER_INFO_TABLE='voter_data'
AWS_REGION_NAME = 'us-east-1'

LAMBDA_UPDATE_VOTE_FUNCTION = 'updateCandidateVote'

# password related
salt = "ece1779"


s3_client = boto3.client('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name='us-east-1')

s3resource  = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name='us-east-1')

cloudwatch_client = boto3.client('cloudwatch',
                                 region_name = "us-east-1",
                                 aws_access_key_id=ACCESS_KEY,
                                 aws_secret_access_key=SECRET_KEY)

lambda_client = boto3.client('lambda',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,region_name=AWS_REGION_NAME)

dynamodb = boto3.resource('dynamodb',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,region_name=AWS_REGION_NAME)
dynamodb_client = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,region_name=AWS_REGION_NAME)


from flask import json
import time
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


start_time = time.time()
testv=verify_voter('kaku0o0','123')

test_event = {"body": {
            "candidate": "a, a"
            }
        }

response = lambda_client.invoke(
            FunctionName=LAMBDA_UPDATE_VOTE_FUNCTION,
            Payload=json.dumps(test_event),
        )

time_count=(time.time() - start_time)
print("--- %s seconds ---" % (time.time() - start_time))


#
f = open("time.txt", "a")
#f.write("upload time: "+str(response.elapsed.total_seconds())+"\n")
f.write(str(time_count)+"\n")
f.close()