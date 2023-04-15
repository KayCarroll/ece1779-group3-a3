import atexit
import boto3
import logging

from flask import Flask

from registapp.constants import *


LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'

dynamodb = boto3.resource('dynamodb',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,region_name=AWS_REGION_NAME)
dynamodb_client = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,region_name=AWS_REGION_NAME)
s3_client = boto3.client('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name=AWS_REGION_NAME)

s3resource  = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name=AWS_REGION_NAME)



logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


app = Flask(__name__)


def close_client():
    dynamodb_client.close()
    logger.info(f'Closed DynamoDB client')


atexit.register(close_client)
from registapp import main
