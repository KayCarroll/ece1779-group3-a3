import json
import logging
import hashlib
from datetime import datetime, timedelta
from flask import redirect, render_template, url_for, request
from flask import session
from registapp import app, dynamodb_client
from registapp.constants import LOG_FORMAT, TIME_FORMAT, VOTING_INFO_TABLE, CANDIDATE_VOTES_TABLE

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


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

@app.route('/create_account', methods=['POST'])
def create_account():
    global input_username
    global input_password
    input_username=request.form.get("username")
    input_password=request.form.get("password")
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
    

    with open('test2.txt', 'w') as f:
       
        f.write(input_username)
        f.write('\n')
        f.write(input_password)
        f.write('\n')
    
    fullname=firstname+lastname
    
    
    with open(input_username+'.txt', 'w') as f:
       
        f.write(firstname)
        f.write('\n')
        f.write(lastname)
        f.write('\n')
        f.write(birthday)
        f.write('\n')
        f.write(address)
        f.write('\n')
        f.write(suite)
        f.write('\n')
        f.write(city)
        f.write('\n')
        f.write(province)
        f.write('\n')
        f.write(postal)
        f.write('\n')

    hashed_pass_db = password_hashing(input_password)
   # db_con =  get_db()
   # cursor= db_con.cursor()
   # #Check the key is not duplicate, if it is, replace the old file
   # cursor.execute("SELECT image_key FROM image_key_table1 WHERE BINARY image_key = BINARY %s GROUP BY image_key",(file_name,))
    #exist = cursor.fetchone()
    # add the key to the list of known keys in the database
   # if exist is None:
      #  cursor.execute("INSERT INTO image_key_table1 VALUES(%s)",(file_name,))
      #  db_con.commit()
        
   
   # file = request.files['my_image']
 
    #print (file)
    #print(file.content_type)
   # print(file.filename)
    #print(file.mimetype)
    #print(file.name)


    #s3_client.upload_fileobj(file, S3_bucket_name, file_name)
    
   
 

    #print(active_list)
    #print(app.config_variables.active_list)
    #invalidate memcache key
   # partition_numb=hash_partition(key=file_name)

  #  active_list_index=route_partition_node(number_active_node=len(active_list),partition_number=partition_numb)



    return render_template('message.html', user_message="Your image has been uploaded successfully!", return_addr='/home')

def password_hashing(password):
    dataBase_password = password + salt
    hashed_password = hashlib.md5(dataBase_password.encode())
    return hashed_password.hexdigest()

