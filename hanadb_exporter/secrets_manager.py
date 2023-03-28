"""
Unitary tests for exporters/secrets_manager.py.

:author: elturkym, schniber

:since: 2021-07-15
"""

import json
import logging

import boto3
import requests
from ec2_metadata import ec2_metadata
from botocore.exceptions import ClientError
from requests.exceptions import HTTPError

LOGGER = logging.getLogger(__name__)


class SecretsManagerError(ValueError):
    """
    Unable to retrieve secret details
    """


def get_db_credentials(secret_name):
    LOGGER.info('retrieving AWS secret details')

    # In this call, we leverage the use of the ec2_metadata python package to read the region name.
    # this package abstracts the requirement to adapt the call to the EC2 Metadata Service depending on the fact that the instance is configures for IMDSv1 or IMDSv2
    region_name = ec2_metadata.region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise SecretsManagerError("Couldn't retrieve secret details") from e
    else:
        # Decrypts secret using the associated KMS CMK.]
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)