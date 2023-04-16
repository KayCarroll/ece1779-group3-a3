import json
import logging
import hashlib
from datetime import datetime, timedelta
from flask import redirect, render_template, url_for, request
from flask import session
from registapp import app, dynamodb_client
from registapp.constants import *

from registapp import dynamodb, dynamodb_client, s3_client, s3resource

salt = "ece1779"
input_username=''
input_password=''
import secrets

app.secret_key = secrets.token_hex(16)

@app.route('/')
def main():
    return render_template('main.html', return_addr='/create_account')


@app.route('/home')
def home():
    return render_template('main.html' , return_addr='/create_account')


@app.route('/information')
def information():

    return render_template('information.html')

@app.route('/create_account')
def account():

    return render_template('create_account.html')


def verify_username(voter_name):
    if not voter_name:
        return False
    table = dynamodb.Table(VOTER_INFO_TABLE)
    response = table.get_item( Key={ 'voter_name': voter_name } )
    if 'Item' in response:
        return True

    else:
        return False


@app.route('/create_account', methods=['POST'])
def create_account():
    global input_username
    global input_password
    input_username=request.form.get("username")
    input_password=request.form.get("password")
    if verify_username(input_username):
        
    #Check if username already in database
        error_message = "Username already exists. Please choose a different username."
        return render_template('create_account.html', error_message=error_message)
    
    #with open('test.txt', 'w') as f:
      #  f.write(input_username)
     #   f.write('\n')
      #  f.write(input_password)
       # f.write('\n')
       
    return redirect(url_for('information'))

@app.route('/information', methods=['POST'])
def next_step():
    
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    birthday = request.form.get("birthday")
    address = request.form.get("address")
    suite = request.form.get("suite")
    city = request.form.get("city")
    province = request.form.get("province")
    postal = request.form.get("postal")
    

    hashed_pass_db = password_hashing(input_password)
    table = dynamodb.Table(VOTER_INFO_TABLE)
    response = table.put_item(
        Item={
            'voter_name': input_username,
            'password': hashed_pass_db,
            "voter_info": f"voterinfo/{input_username}.txt",
            "already_voted": "False"
        }
    )

    
    
    s3object = s3resource.Object(S3_bucket_name, f'voterinfo/{input_username}.txt')
    content=f'{firstname}\n{lastname}\n{birthday}\n{address}\n{suite}\n{city}\n{province}\n{postal}\n'
    s3object.put(Body=content)




    return render_template('message.html', user_message="You registered successfully!", return_addr='/home')

def password_hashing(password):
    dataBase_password = password + salt
    hashed_password = hashlib.md5(dataBase_password.encode())
    return hashed_password.hexdigest()

