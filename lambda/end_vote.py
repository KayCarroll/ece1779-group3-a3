import boto3
import logging
import json

from datetime import datetime

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
VOTING_INFO_TABLE = 'voting_info'
CANDIDATE_VOTES_TABLE = 'Candidate_Votes'
AWS_REGION_NAME = 'us-east-1'
dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION_NAME)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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



def lambda_handler(event, context):
    logger.debug(f'Triggered lambda to end vote with event: {event}')
    vote_name = event['vote_name']
    vote_info = get_vote(vote_name)

    if vote_info: 
        if vote_info['currently_active']['S'] == 'True':
            end_time = datetime.utcnow().strftime(TIME_FORMAT)
            response = dynamodb_client.update_item(TableName=VOTING_INFO_TABLE,
                                                   Key={'election_name': {'S': vote_name}},
                                                   ExpressionAttributeValues={':et': {'S': end_time},
                                                                              ':ca': {'S': 'False'}},
                                                   UpdateExpression=f'SET end_time = :et, currently_active = :ca')
            logger.info(f'Ended current vote: {vote_name} at {end_time}')
        else:
            end_time = vote_info['end_time']['S']
            logger.info(f'Vote {vote_name} already ended at {end_time}')

    return {'statusCode': 200,
            'body': json.dumps(f'Vote {vote_name} ended')}
