"""""
Description:  Enables S3 default encryption and set to AES-256 when a user creates a bucket.
Services: Amazon Cloudwatch Events (trigger), AWS Simple Storage Service (S3), AWS Identity and Access Management (IAM)
Runtime: Python 3.8
"""

import logging
import os
import json
import boto3


def lambda_handler(event, context):
    setup_logging()
    log.info('Lambda received event:')
    log.info(json.dumps(event))
    client = boto3.client('s3')
    bucket_name = event['detail']['requestParameters']['bucketName']
    try:
        if "CreateBucket" in event["detail"]["eventName"]:
            existing_encryption = client.get_bucket_encryption(Bucket=bucket_name)
            log.info('Encryption is enabled already on bucket: ' + bucket_name)
            print('Encryption is enabled already on bucket')
            return
    except client.exceptions.ClientError:
        # Enable encryption here as  client.get_bucket_encryption() will throw exception if encryption isn't enabled
        # on bucket creation
        log.info('Enabling encryption on bucket :' + bucket_name)
        print('Enabling encryption on bucket')
        client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        status = 200
        return {
            'statusCode': status,
            'details': 'Default encryption enabled',
            'bucket Name': bucket_name
        }


def setup_logging():
    """
    Logging Function.
    Creates a global log object and sets its level.
    """
    global log
    log = logging.getLogger()
    log_levels = {'INFO': 20, 'WARNING': 30, 'ERROR': 40}

    if 'logging_level' in os.environ:
        log_level = os.environ['logging_level'].upper()
        if log_level in log_levels:
            log.setLevel(log_levels[log_level])
        else:
            log.setLevel(log_levels['ERROR'])
            log.error("The logging_level environment variable is not set to INFO, WARNING, or \
                        ERROR.  The log level is set to ERROR")
    else:
        log.setLevel(log_levels['ERROR'])
    log.info('Logging setup complete - set to log level ' + str(log.getEffectiveLevel()))
