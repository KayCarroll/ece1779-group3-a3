import json
import logging
import boto3

from datetime import datetime, timedelta
from flask import redirect, render_template, url_for, request

from adminapp import app, dynamodb_client, events_client, lambda_client, dynamodb_resource
from adminapp.constants import (AWS_REGION_NAME, LOG_FORMAT, TIME_FORMAT, VOTING_INFO_TABLE,
                                CANDIDATE_VOTES_TABLE, VOTER_DATA_TABLE, END_VOTE_LAMBDA, LAMBDA_ARN)

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


def get_candidate_votes(candidates):
    for candidate in candidates:
        response = dynamodb_client.query(TableName=CANDIDATE_VOTES_TABLE,
                                         ExpressionAttributeValues={':name': {'S': candidate['name']}},
                                         KeyConditionExpression='candidate_name = :name')
        if response['Items']:
            candidate['total_vote'] = response['Items'][0]['total_vote']['N']
        else:
            logger.warning(f'No entry in the candidate votes table found for candidate {candidate["name"]}')
            candidate['total_vote'] = 0
    return candidates


def get_past_votes():
    response = dynamodb_client.scan(TableName=VOTING_INFO_TABLE, Select='ALL_ATTRIBUTES',
                                    FilterExpression='currently_active = :activeval',
                                    ExpressionAttributeValues={':activeval': {'S': 'False'}})

    past_votes = []
    for vote in response['Items']:
        past_votes.append({'election_name': vote['election_name']['S'],
                           'start_time':  vote['start_time']['S'],
                           'end_time':  vote['end_time']['S']})
    past_votes.sort(key=lambda x:datetime.strptime(x['start_time'], TIME_FORMAT), reverse=True)
    return past_votes


def get_vote(vote_name):
    response = dynamodb_client.query(TableName=VOTING_INFO_TABLE,
                                     ExpressionAttributeValues={':name': {'S': vote_name}},
                                     KeyConditionExpression='election_name = :name')

    vote_info = None
    if response['Items']:
        vote_info = response['Items'][0]
    else:
        logger.warning(f'No vote found with name {vote_name}')
    return vote_info

def remove_all_registered_voters():
    
    table = dynamodb_resource.Table(VOTER_DATA_TABLE)

    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan['Items']:
            print("EACH: ")
            print(each)
            batch.delete_item(Key={
                "voter_name": each["voter_name"]
            })

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
        candidates = get_candidate_votes(candidates)
        logger.debug(f'candidates: {candidates}')
    else:
        disable = True

    return render_template('current.html', vote_name=vote_name, start_time=start_time,
                           end_time=end_time, candidates=candidates, disable=disable)


@app.route('/end_current_vote', methods=['POST'])
def end_current_vote():
    election_name = request.form['votename']
    end_time = datetime.utcnow().strftime(TIME_FORMAT)
    response = dynamodb_client.update_item(TableName=VOTING_INFO_TABLE,
                                           Key={'election_name': {'S': election_name}},
                                           ExpressionAttributeValues={':et': {'S': end_time},
                                                                      ':ca': {'S': 'False'}},
                                           UpdateExpression=f'SET end_time = :et, currently_active = :ca')
    logger.debug(f'Ended current vote: {election_name} at {end_time}')
    return redirect(url_for('current'))


def schedule_end_vote(vote_name, end_time):
    rule_name = f'endVote{vote_name.replace(" ", "")}'
    logger.info('New rule name: {rule_name}')
    schedule_end_cron_str = f'cron({end_time.minute} {end_time.hour} {end_time.day} {end_time.month} ? {end_time.year})'
    res = events_client.put_rule(Name=rule_name, ScheduleExpression=schedule_end_cron_str, State='ENABLED')
    lambda_client.add_permission(FunctionName=END_VOTE_LAMBDA, StatementId=f'{rule_name}-Event',
                                 Action='lambda:InvokeFunction', Principal='events.amazonaws.com',
                                 SourceArn=res['RuleArn'])

    target_input = json.dumps({'vote_name': vote_name, 'rule_name': rule_name})
    res = events_client.put_targets(Rule=rule_name, Targets=[{'Id': END_VOTE_LAMBDA, 'Arn': LAMBDA_ARN,
                                                              'Input': target_input}])


@app.route('/start_new_vote', methods=['POST'])
def start_new_vote():
    remove_all_registered_voters()
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

    for candidate in candidates.values():
        dynamodb_client.put_item(TableName=CANDIDATE_VOTES_TABLE,
                                 Item={'candidate_name': {'S': candidate['name']},
                                       'total_vote': {'N': '0'}})

    vote_duration = request.form.get('voteduration').split(':')
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=int(vote_duration[0]),
                                      minutes=int(vote_duration[1]))

    vote_name = request.form.get('votename')
    dynamodb_client.put_item(TableName=VOTING_INFO_TABLE,
                             Item={'election_name': {'S': vote_name},
                                   'candidates': {'S': json.dumps(candidates)},
                                   'start_time': {'S': start_time.strftime(TIME_FORMAT)},
                                   'end_time': {'S': end_time.strftime(TIME_FORMAT)},
                                   'currently_active': {'S': 'True'}})
    logger.info(candidates)
    schedule_end_vote(vote_name, end_time)
    remove_all_registered_voters()
    return redirect(url_for('create'))


@app.route('/past')
def past():
    past_votes = get_past_votes()
    logger.info(f'past_votes: {past_votes}')
    return render_template('past.html', past_votes=past_votes)


@app.route('/results', methods=['POST'])
def results():
    vote_name = request.form['votename']
    start_time = ''
    end_time = ''
    candidates = []

    current_vote = get_vote(vote_name)
    if current_vote:
        start_time = current_vote['start_time']['S']
        end_time = current_vote['end_time']['S']
        candidates = list(json.loads(current_vote['candidates']['S']).values())
        candidates = get_candidate_votes(candidates)
        logger.debug(f'candidates: {candidates}')

    return render_template('results.html', vote_name=vote_name, start_time=start_time,
                           end_time=end_time, candidates=candidates)
