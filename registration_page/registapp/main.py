import json
import logging

from datetime import datetime, timedelta
from flask import redirect, render_template, url_for, request

from registapp import app, dynamodb_client
from registapp.constants import LOG_FORMAT, TIME_FORMAT, VOTING_INFO_TABLE, CANDIDATE_VOTES_TABLE

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)




@app.route('/')
def main():
    return render_template('main.html', return_addr='/information')


@app.route('/home')
def home():
    return render_template('main.html' , return_addr='/information')


@app.route('/information')
def information():

    return render_template('information.html')


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
    with open('readme.txt', 'w') as f:
       
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
