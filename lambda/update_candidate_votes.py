import boto3
import logging
import json

CANDIDATE_VOTES_TABLE = 'Candidate_Votes'
AWS_REGION_NAME = 'us-east-1'
dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION_NAME)

logger = logging.getLogger(__name__)

def lambda_handler(event, context):

    # logger.warning(f'event: {event}')
    candidate = json.loads(event['body'])['candidate']
    logger.info(f'Received request to add vote for candidate {candidate}')
    res = dynamodb_client.update_item(TableName=CANDIDATE_VOTES_TABLE,
                                      Key={'candidate_name': {'S': candidate}},
                                      ExpressionAttributeNames={'#votes': 'total_vote'},
                                      ExpressionAttributeValues={':increase': {'N': '1'}},
                                      UpdateExpression='ADD #votes :increase',
                                      ReturnValues='UPDATED_NEW')
    logger.info(f'Updated total vote for candidate {candidate}: {res}')

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
