db_config = {'user': 'admin',
             'password': '12345678',
             'host': 'assignment-database.c9rxb7sabfel.us-east-1.rds.amazonaws.com',
             'database': 'image_key'}

S3_bucket_name = "ece1779-a3-bucket"
ACCESS_KEY = "AKIATP2NMF23IIODM2W5"
SECRET_KEY = "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"
VOTING_INFO_TABLE = 'voting_info'
VOTER_INFO_TABLE='voter_data'
AWS_REGION_NAME = 'us-east-1'

memcache_option = "manual"
frontend_base_url = "http://127.0.0.1:5000"
manager_base_url = "http://127.0.0.1:5001"
auto_scaler_base_url = "http://127.0.0.1:5002"

CLOUDWATCH_NAMESPACE = "MemCache Metrics 2"