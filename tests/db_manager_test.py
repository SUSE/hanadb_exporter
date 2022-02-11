"""
Unitary tests for exporters/db_manager.py.

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.com

:since: 2019-10-25
"""

# pylint:disable=C0103,C0111,W0212,W0611

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from unittest import mock
except ImportError:
    import mock

sys.modules['shaptools'] = mock.MagicMock()
from hanadb_exporter import db_manager


class TestDatabaseManager(object):
    """
    Unitary tests for hanadb_exporter/db_manager.py.
    """

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.HdbConnector')
    def setup(self, mock_hdb):
        """
        Test setUp.
        """

        self._db_manager = db_manager.DatabaseManager()
        mock_hdb.assert_called_once_with()

    @mock.patch('hanadb_exporter.db_manager.utils.format_query_result')
    def test_get_tenants_port(self, mock_format_query):
        self._db_manager._system_db_connector = mock.Mock()
        self._db_manager._system_db_connector.query.return_value = 'result'
        ports = ['30040', '30041']
        dbs = ['PRD', 'QAS']
        mock_format_query.return_value = [
            {'DATABASE_NAME': dbs[0], 'SQL_PORT': ports[0]},
            {'DATABASE_NAME': dbs[1], 'SQL_PORT': ports[1]},
            {'DATABASE_NAME': 'SYSTEMDB', 'SQL_PORT': '30013'}]

        for i, data in enumerate(self._db_manager._get_tenants_port()):
            assert data[0] == dbs[i]
            assert data[1] == int(ports[i])
        assert i == 1 # Check only the ports 30040 and 30041 are yielded

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.HdbConnector')
    def test_connect_tenants(self, mock_hdb):

        self._db_manager._get_tenants_port = mock.Mock(return_value=[
            ('db1', 1), ('db2', 2),('db3', 3)])

        mock_conn1 = mock.Mock()
        mock_conn2 = mock.Mock()
        mock_conn3 = mock.Mock()

        mock_hdb.side_effect = [mock_conn1, mock_conn2, mock_conn3]

        connection_data = {'mock_data': 'data'}

        self._db_manager._connect_tenants('10.10.10.10', connection_data)

        assert mock_hdb.call_count == 3

        mock_conn1.connect.assert_called_once_with('10.10.10.10', 1, **connection_data)
        mock_conn2.connect.assert_called_once_with('10.10.10.10', 2, **connection_data)
        mock_conn3.connect.assert_called_once_with('10.10.10.10', 3, **connection_data)

        assert self._db_manager._db_connectors == [mock_conn1, mock_conn2, mock_conn3]

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.HdbConnector')
    def test_connect_tenants_userkey(self, mock_hdb):

        self._db_manager._get_tenants_port = mock.Mock(return_value=[
            ('db1', 1), ('db2', 2),('db3', 3)])

        mock_conn1 = mock.Mock()
        mock_conn2 = mock.Mock()
        mock_conn3 = mock.Mock()

        mock_hdb.side_effect = [mock_conn1, mock_conn2, mock_conn3]

        connection_data = {'mock_data': 'data', 'userkey': 'userkey'}
        updated_connection_data = [
            {'mock_data': 'data', 'userkey': 'userkey', 'databaseName': 'db1'},
            {'mock_data': 'data', 'userkey': 'userkey', 'databaseName': 'db2'},
            {'mock_data': 'data', 'userkey': 'userkey', 'databaseName': 'db3'}
        ]

        self._db_manager._connect_tenants('10.10.10.10', connection_data)

        assert mock_hdb.call_count == 3

        mock_conn1.connect.assert_called_once_with('10.10.10.10', 1, **updated_connection_data[0])
        mock_conn2.connect.assert_called_once_with('10.10.10.10', 2, **updated_connection_data[1])
        mock_conn3.connect.assert_called_once_with('10.10.10.10', 3, **updated_connection_data[2])

        assert self._db_manager._db_connectors == [mock_conn1, mock_conn2, mock_conn3]

    @mock.patch('logging.Logger.warn')
    @mock.patch('hanadb_exporter.db_manager.hdb_connector.connectors.base_connector')
    @mock.patch('hanadb_exporter.db_manager.hdb_connector.HdbConnector')
    def test_connect_tenants_error_connecting(self, mock_hdb, mock_connector, mock_warn):

        self._db_manager._get_tenants_port = mock.Mock(return_value=[
            ('db1', 1), ('db2', 2),('db3', 3)])

        mock_connector.ConnectionError = Exception
        mock_conn1 = mock.Mock()
        mock_conn2 = mock.Mock()
        mock_conn3 = mock.Mock()
        mock_conn3.connect.side_effect = mock_connector.ConnectionError('err')

        mock_hdb.side_effect = [mock_conn1, mock_conn2, mock_conn3]

        connection_data = {'mock_data': 'data', 'userkey': 'userkey'}
        updated_connection_data = [
            {'mock_data': 'data', 'userkey': 'userkey', 'databaseName': 'db1'},
            {'mock_data': 'data', 'userkey': 'userkey', 'databaseName': 'db2'},
            {'mock_data': 'data', 'userkey': 'userkey', 'databaseName': 'db3'}
        ]

        self._db_manager._connect_tenants('10.10.10.10', connection_data)

        assert mock_hdb.call_count == 3

        mock_conn1.connect.assert_called_once_with('10.10.10.10', 1, **updated_connection_data[0])
        mock_conn2.connect.assert_called_once_with('10.10.10.10', 2, **updated_connection_data[1])
        mock_conn3.connect.assert_called_once_with('10.10.10.10', 3, **updated_connection_data[2])

        assert self._db_manager._db_connectors == [mock_conn1, mock_conn2]
        mock_warn.assert_called_once_with(
            'Could not connect to TENANT database %s with error: %s', 'db3', str('err'))

    def test_get_connection_data_invalid_data(self):

        with pytest.raises(ValueError) as err:
            self._db_manager._get_connection_data(None, '', '')
        assert 'Provided user data is not valid. userkey or user/password pair must be provided' \
            in str(err.value)

        with pytest.raises(ValueError) as err:
            self._db_manager._get_connection_data(None, 'user', '')
        assert 'Provided user data is not valid. userkey or user/password pair must be provided' \
            in str(err.value)

        with pytest.raises(ValueError) as err:
            self._db_manager._get_connection_data(None, '', 'pass')
        assert 'Provided user data is not valid. userkey or user/password pair must be provided' \
            in str(err.value)

    @mock.patch('hanadb_exporter.db_manager.hdb_connector')
    def test_get_connection_data_not_supported(self, mock_api):

        mock_api.API = 'pyhdb'
        with pytest.raises(db_manager.UserKeyNotSupportedError) as err:
            self._db_manager._get_connection_data('userkey', '', '')
        assert 'userkey usage is not supported with pyhdb connector, hdbcli must be installed' \
            in str(err.value)

    @mock.patch('hanadb_exporter.db_manager.hdb_connector')
    @mock.patch('logging.Logger.warn')
    @mock.patch('logging.Logger.info')
    def test_get_connection_data_userkey(self, logger,logger_warn, mock_api):

        mock_api.API = 'dbapi'
        connection_data = self._db_manager._get_connection_data('userkey', '', '')
        assert connection_data == {
            'userkey': 'userkey', 'user': '', 'password': '', 'RECONNECT': 'FALSE',
            'encrypt': False, 'sslValidateCertificate': False, 'sslTrustStore': None}
        logger.assert_called_once_with(
            'stored user key %s will be used to connect to the database', 'userkey')
        assert logger_warn.call_count == 0

    @mock.patch('hanadb_exporter.db_manager.hdb_connector')
    @mock.patch('logging.Logger.warn')
    @mock.patch('logging.Logger.info')
    def test_get_connection_data_userkey_warn(self, logger,logger_warn, mock_api):

        mock_api.API = 'dbapi'
        connection_data = self._db_manager._get_connection_data('userkey', 'user', '')
        assert connection_data == {
            'userkey': 'userkey', 'user': 'user', 'password': '', 'RECONNECT': 'FALSE',
            'encrypt': False, 'sslValidateCertificate': False, 'sslTrustStore': None}
        logger.assert_called_once_with(
            'stored user key %s will be used to connect to the database', 'userkey')
        logger_warn.assert_called_once_with(
            'userkey will be used to create the connection. user/password are omitted')

    @mock.patch('hanadb_exporter.db_manager.hdb_connector')
    @mock.patch('logging.Logger.info')
    def test_get_connection_data_pass(self, logger, mock_api):
        mock_api.API = 'dbapi'
        connection_data = self._db_manager._get_connection_data(None, 'user', 'pass')
        assert connection_data == {
            'userkey': None, 'user': 'user', 'password': 'pass', 'RECONNECT': 'FALSE',
            'encrypt': False, 'sslValidateCertificate': False, 'sslTrustStore': None}
        logger.assert_called_once_with(
            'user/password combination will be used to connect to the database')

    @mock.patch('certifi.where')
    @mock.patch('hanadb_exporter.db_manager.hdb_connector')
    @mock.patch('logging.Logger.info')
    def test_get_connection_ssl(self, logger, mock_api, mock_where):
        mock_where.return_value = 'my.pem'
        mock_api.API = 'dbapi'
        connection_data = self._db_manager._get_connection_data(
            None, 'user', 'pass', ssl=True, ssl_validate_cert=True)
        assert connection_data == {
            'userkey': None, 'user': 'user', 'password': 'pass', 'RECONNECT': 'FALSE',
            'encrypt': True, 'sslValidateCertificate': True, 'sslTrustStore': 'my.pem'}
        logger.assert_has_calls([
            mock.call('user/password combination will be used to connect to the database'),
            mock.call('Using ssl connection...')
        ])

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.connectors.base_connector')
    @mock.patch('logging.Logger.error')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_start_timeout(self, mock_time, mock_sleep, mock_logger, mock_exception):

        self._db_manager._get_connection_data = mock.Mock()
        connection_data = {'mock_data': 'data'}
        self._db_manager._get_connection_data.return_value = connection_data

        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err')]

        # Method under test
        with pytest.raises(mock_exception.ConnectionError) as err:
            self._db_manager.start(
                '10.10.10.10', 30013, user='user', password='pass', multi_tenant=False, timeout=2)

        assert 'timeout reached connecting the System database' in str(err.value)

        self._db_manager._system_db_connector.connect.assert_has_calls([
            mock.call('10.10.10.10', 30013, **connection_data),
            mock.call('10.10.10.10', 30013, **connection_data),
            mock.call('10.10.10.10', 30013, **connection_data)
        ])

        mock_sleep.assert_has_calls([
            mock.call(15),
            mock.call(15),
            mock.call(15)
        ])

        mock_logger.assert_has_calls([
            mock.call('the connection to the system database failed. error message: %s', 'err'),
            mock.call('the connection to the system database failed. error message: %s', 'err'),
            mock.call('the connection to the system database failed. error message: %s', 'err')
        ])

        assert self._db_manager._db_connectors == []

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.connectors.base_connector')
    @mock.patch('logging.Logger.error')
    @mock.patch('time.time')
    def test_start_invalid_key(self, mock_time, mock_logger, mock_exception):

        self._db_manager._get_connection_data = mock.Mock()
        connection_data = {'mock_data': 'data'}
        self._db_manager._get_connection_data.return_value = connection_data

        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()
        self._db_manager._connect_tenants = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('Error: Invalid value for KEY')]

        # Method under test
        with pytest.raises(mock_exception.ConnectionError) as err:
            self._db_manager.start(
                '10.10.10.10', 30013, user='user', password='pass', multi_tenant=False, timeout=2)

        assert 'provided userkey is not valid. Check if dbapi is installed correctly' in str(err.value)

        self._db_manager._system_db_connector.connect.assert_called_once_with(
            '10.10.10.10', 30013, **connection_data)

        mock_logger.assert_called_once_with(
            'the connection to the system database failed. error message: %s',
            'Error: Invalid value for KEY')

        self._db_manager._connect_tenants.assert_not_called()

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.connectors.base_connector')
    @mock.patch('logging.Logger.error')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_start_correct(self, mock_time, mock_sleep, mock_logger, mock_exception):

        self._db_manager._get_connection_data = mock.Mock()
        connection_data = {'mock_data': 'data'}
        self._db_manager._get_connection_data.return_value = connection_data

        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()
        self._db_manager._connect_tenants = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err'),
            None]

        self._db_manager.start(
            '10.10.10.10', 30013, user='user', password='pass', multi_tenant=False, timeout=2)

        self._db_manager._system_db_connector.connect.assert_has_calls([
            mock.call('10.10.10.10', 30013, **connection_data),
            mock.call('10.10.10.10', 30013, **connection_data),
            mock.call('10.10.10.10', 30013, **connection_data)
        ])

        mock_sleep.assert_has_calls([
            mock.call(15),
            mock.call(15)
        ])

        mock_logger.assert_has_calls([
            mock.call('the connection to the system database failed. error message: %s', 'err'),
            mock.call('the connection to the system database failed. error message: %s', 'err')
        ])

        assert self._db_manager._db_connectors == [self._db_manager._system_db_connector]
        self._db_manager._connect_tenants.assert_not_called()

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.connectors.base_connector')
    @mock.patch('logging.Logger.error')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_start_correct_multitenant(self, mock_time, mock_sleep, mock_logger, mock_exception):

        self._db_manager._get_connection_data = mock.Mock()
        connection_data = {'mock_data': 'data'}
        self._db_manager._get_connection_data.return_value = connection_data

        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()
        self._db_manager._connect_tenants = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err'),
            None]

        self._db_manager.start(
            '10.10.10.10', 30013, user='user', password='pass', multi_tenant=True, timeout=2)

        self._db_manager._system_db_connector.connect.assert_has_calls([
            mock.call('10.10.10.10', 30013, **connection_data),
            mock.call('10.10.10.10', 30013, **connection_data),
            mock.call('10.10.10.10', 30013, **connection_data)
        ])

        mock_sleep.assert_has_calls([
            mock.call(15),
            mock.call(15)
        ])

        mock_logger.assert_has_calls([
            mock.call('the connection to the system database failed. error message: %s', 'err'),
            mock.call('the connection to the system database failed. error message: %s', 'err')
        ])

        assert self._db_manager._db_connectors == [self._db_manager._system_db_connector]
        self._db_manager._connect_tenants.assert_called_once_with('10.10.10.10', connection_data)


    def test_get_connectors(self):
        self._db_manager._db_connectors = 'conns'
        assert 'conns' == self._db_manager.get_connectors()
