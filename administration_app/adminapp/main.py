import json
import logging

from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from flask import render_template, url_for, request, g

from adminapp import app, dynamodb_client
from adminapp.constants import LOG_FORMAT, TIME_FORMAT, VOTING_INFO_TABLE

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


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
    # response = dynamodb_client.query(TableName=VOTING_INFO_TABLE, Select='ALL_ATTRIBUTES',
    #                                  KeyConditionExpression='currently_active = :activeval',
    #                                  ExpressionAttributeValues={':activeval': {'S': 'True'}})
    # logger.info(response)

    return render_template('current.html')



@app.route('/start_new_vote', methods=['POST'])
def start_new_vote():
    candidates = {}
    for key, val in request.form.items():
        if '-' in key:
            candidate_id, field_num = key.split('-')
            if val:
                if candidate_id not in candidates:
                    candidates[candidate_id] = {'name': '', 'association': ''}

                if field_num == '1':
                    candidates[candidate_id]['name'] = val
                elif field_num == '2':
                    candidates[candidate_id]['name'] += f', {val}'
                elif field_num == '3':
                    candidates[candidate_id]['association'] = val

    vote_duration = request.form.get('voteduration').split(':')
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=int(vote_duration[0]),
                                      minutes=int(vote_duration[1]),
                                      seconds=int(vote_duration[2]))

    dynamodb_client.put_item(TableName=VOTING_INFO_TABLE,
                             Item={'election_name': {'S': request.form.get('votename')},
                                   'candidates': {'S': json.dumps(candidates)},
                                   'start_time': {'S': start_time.strftime(TIME_FORMAT)},
                                   'end_time': {'S': end_time.strftime(TIME_FORMAT)},
                                   'currently_active': {'S': 'True'}})

    logger.info(candidates)

    return render_template('create.html')
