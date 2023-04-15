import boto3
import json
import logging
# import time

# from datetime import date, datetime, timedelta
from boto3.dynamodb.conditions import Attr, Key

AWS_REGION_NAME = 'us-east-1'
TABLES_CONFIG_FILE = 'tables_config.json'
LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
ACCESS_KEY = "AKIARYPZNG6KRLLMQZ3X"
SECRET_KEY = "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"
dynamodb_client = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=AWS_REGION_NAME)


def get_tables_config():
    with open(TABLES_CONFIG_FILE, 'r') as f:
        tables_config = json.load(f)
    return tables_config


def create_table(table_config):
    try:
        dynamodb_client.create_table(**table_config)
    except dynamodb_client.exceptions.ResourceInUseException:
        logger.warning(f'Table {table_config["TableName"]} already exist, skip creation.')


if __name__ == '__main__':
    for table_config in get_tables_config():
        create_table(table_config)
