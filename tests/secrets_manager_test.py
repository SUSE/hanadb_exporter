"""
Unitary tests for exporters/secrets_manager.py.

:author: elturkym, schniber

:since: 2021-07-15
"""

import json

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from hanadb_exporter import secrets_manager
from botocore.exceptions import ClientError
from requests.exceptions import HTTPError


class TestSecretsManager(object):
    """
    Unitary tests for hanadb_exporter/secrets_manager.py.
    """

    @mock.patch('hanadb_exporter.secrets_manager.LOGGER')
    @mock.patch('hanadb_exporter.secrets_manager.requests')
    @mock.patch('hanadb_exporter.secrets_manager.boto3.session')
    def test_get_db_credentials(self, mock_boto3, mock_requests, mock_logger):
        mock_ec2_response = mock.Mock()
        mock_requests.get.return_value = mock_ec2_response
        mock_ec2_response.json.return_value = json.loads('{"region":"test_region"}')
        mock_session = mock.Mock()
        mock_sm_client = mock.Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_sm_client
        mock_sm_client.get_secret_value.return_value = json.loads(
            '{"SecretString" : "{\\"username\\": \\"db_user\\", \\"password\\":\\"db_pass\\"}"}')

        actual_secret = secrets_manager.get_db_credentials("test_secret")

        mock_session.client.assert_called_once_with(service_name='secretsmanager', region_name='test_region')
        mock_sm_client.get_secret_value.assert_called_once_with(SecretId='test_secret')
        mock_logger.info.assert_has_calls([
            mock.call('retrieving AWS secret details')
        ])
        assert actual_secret['username'] == 'db_user'
        assert actual_secret['password'] == 'db_pass'

    @mock.patch('hanadb_exporter.secrets_manager.LOGGER')
    @mock.patch('hanadb_exporter.secrets_manager.requests')
    @mock.patch('hanadb_exporter.secrets_manager.boto3.session')
    def test_get_db_credentials_imdsv2(self, mock_boto3, mock_requests, mock_logger):
        mock_ec2_unauthorized = mock.Mock()
        mock_ec2_unauthorized.status_code = 401

        mock_ec2_response = mock.Mock()
        mock_ec2_response.json.return_value = json.loads('{"region":"test_region_imdsv2"}')

        mock_requests.get.side_effect = [mock_ec2_unauthorized, mock_ec2_response]

        mock_ec2_put = mock.Mock()
        mock_ec2_put.content = 'my-test-token'

        mock_requests.put.return_value = mock_ec2_put

        mock_session = mock.Mock()
        mock_sm_client = mock.Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_sm_client
        mock_sm_client.get_secret_value.return_value = json.loads(
            '{"SecretString" : "{\\"username\\": \\"db_user\\", \\"password\\":\\"db_pass\\"}"}')

        actual_secret = secrets_manager.get_db_credentials("test_secret")

        mock_session.client.assert_called_once_with(service_name='secretsmanager', region_name='test_region_imdsv2')
        mock_sm_client.get_secret_value.assert_called_once_with(SecretId='test_secret')
        mock_logger.info.assert_has_calls([
            mock.call('retrieving AWS secret details')
        ])

        mock_requests.get.assert_has_calls([
            mock.call("http://169.254.169.254/latest/dynamic/instance-identity/document"),
            mock.call("http://169.254.169.254/latest/dynamic/instance-identity/document",
                      headers={'X-aws-ec2-metadata-token': 'my-test-token'})
        ])

        mock_requests.put.assert_called_with("http://169.254.169.254/latest/api/token",
                                             headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"})

        assert actual_secret['username'] == 'db_user'
        assert actual_secret['password'] == 'db_pass'

    @mock.patch('hanadb_exporter.secrets_manager.requests')
    def test_get_db_credentials_ec2_request_error(self, mock_requests):
        ec2_info_response = mock.Mock()
        mock_requests.get.return_value = ec2_info_response
        ec2_info_response.raise_for_status.side_effect=HTTPError

        with pytest.raises(secrets_manager.SecretsManagerError) as err:
            secrets_manager.get_db_credentials("test_secret")
        assert 'EC2 information request failed' in str(err.value)

    @mock.patch('hanadb_exporter.secrets_manager.requests')
    @mock.patch('hanadb_exporter.secrets_manager.boto3.session')
    def test_get_db_credentials_secret_request_error(self, mock_boto3, mock_requests):
        mock_ec2_response = mock.Mock()
        mock_requests.get.return_value = mock_ec2_response
        mock_ec2_response.json.return_value = json.loads('{"region":"test_region"}')
        mock_session = mock.Mock()
        mock_sm_client = mock.Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_sm_client
        mock_sm_client.get_secret_value.side_effect = ClientError({}, "test_operation")

        with pytest.raises(secrets_manager.SecretsManagerError) as err:
            secrets_manager.get_db_credentials("test_secret")
        assert 'Couldn\'t retrieve secret details' in str(err.value)