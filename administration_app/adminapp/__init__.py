import atexit
import boto3
import logging

from flask import Flask

from adminapp.constants import AWS_REGION_NAME, LOG_FORMAT, ACCESS_KEY, SECRET_KEY

AWS_REGION_NAME = 'us-east-1'
LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


dynamodb_client = boto3.client('dynamodb',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=AWS_REGION_NAME)
events_client = boto3.client('events',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=AWS_REGION_NAME)
lambda_client = boto3.client('lambda',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=AWS_REGION_NAME)

app = Flask(__name__)


def close_client():
    dynamodb_client.close()
    logger.info(f'Closed DynamoDB client')
    events_client.close()
    logger.info(f'Closed Events client')
    lambda_client.close()
    logger.info(f'Closed Lambda client')


atexit.register(close_client)
from adminapp import main
