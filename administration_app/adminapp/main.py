import json
import logging

from datetime import datetime, timedelta
from flask import redirect, render_template, url_for, request

from adminapp import app, dynamodb_client
from adminapp.constants import LOG_FORMAT, TIME_FORMAT, VOTING_INFO_TABLE

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def get_current_vote():
    response = dynamodb_client.scan(TableName=VOTING_INFO_TABLE, Select='ALL_ATTRIBUTES',
                                    FilterExpression='currently_active = :activeval',
                                    ExpressionAttributeValues={':activeval': {'S': 'True'}})
    logger.debug(response)

    current_vote = None
    if len(response['Items']) == 1:
        current_vote = response['Items'][0]
    elif response['Items']:
        logger.warning(f'There is more than one currently active vote!')
    else:
        logger.info('There are no currently active votes.')

    return current_vote


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/home')
def home():
    return render_template('main.html')


@app.route('/create')
def create():
    current_vote = get_current_vote()
    disable = current_vote is not None
    return render_template('create.html', disable=disable)


@app.route('/current')
def current():
    vote_name = ''
    start_time = ''
    end_time = ''
    candidates = []
    disable = False

    current_vote = get_current_vote()
    if current_vote:
        vote_name = current_vote['election_name']['S']
        start_time = current_vote['start_time']['S']
        end_time = current_vote['end_time']['S']
        candidates = list(json.loads(current_vote['candidates']['S']).values())
        logger.debug(candidates)
    else:
        disable = True

    return render_template('current.html', vote_name=vote_name, start_time=start_time,
                           end_time=end_time, candidates=candidates, disable=disable)


@app.route('/end_current_vote', methods=['POST'])
def end_current_vote():
    election_name = request.form["votename"]
    end_time = datetime.utcnow().strftime(TIME_FORMAT)
    response = dynamodb_client.update_item(TableName=VOTING_INFO_TABLE,
                                           Key={'election_name': {'S': election_name}},
                                           ExpressionAttributeValues={':et': {'S': end_time},
                                                                      ':ca': {'S': 'False'}},
                                           UpdateExpression=f'SET end_time = :et, currently_active = :ca')
    logger.debug(f'Ended current vote: {election_name} at {end_time}')
    return redirect(url_for('current'))


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
    return redirect(url_for('create'))
