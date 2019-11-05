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
        mock_format_query.return_value = [{'SQL_PORT': ports[0]}, {'SQL_PORT': ports[1]}]

        for i, port in enumerate(self._db_manager._get_tenants_port()):
            assert port == int(ports[i])

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.HdbConnector')
    def test_connect_tenants(self, mock_hdb):

        self._db_manager._get_tenants_port = mock.Mock(return_value=[1, 2, 3])

        mock_conn1 = mock.Mock()
        mock_conn2 = mock.Mock()
        mock_conn3 = mock.Mock()

        mock_hdb.side_effect = [mock_conn1, mock_conn2, mock_conn3]

        self._db_manager._connect_tenants('10.10.10.10', 'SYSTEM', 'pass')

        assert mock_hdb.call_count == 3

        mock_conn1.connect.assert_called_once_with(
            '10.10.10.10', 1, user='SYSTEM', password='pass', RECONNECT='FALSE')
        mock_conn2.connect.assert_called_once_with(
            '10.10.10.10', 2, user='SYSTEM', password='pass', RECONNECT='FALSE')
        mock_conn3.connect.assert_called_once_with(
            '10.10.10.10', 3, user='SYSTEM', password='pass', RECONNECT='FALSE')

        assert self._db_manager._db_connectors == [mock_conn1, mock_conn2, mock_conn3]

    @mock.patch('hanadb_exporter.db_manager.hdb_connector.connectors.base_connector')
    @mock.patch('logging.Logger.error')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_start_timeout(self, mock_time, mock_sleep, mock_logger, mock_exception):
        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err')]

        with pytest.raises(mock_exception.ConnectionError) as err:
            self._db_manager.start(
                '10.10.10.10', 30013, 'user', 'pass', multi_tenant=False, timeout=2)

        assert 'timeout reached connecting the System database' in str(err.value)

        self._db_manager._system_db_connector.connect.assert_has_calls([
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE'),
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE'),
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE')
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
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_start_correct(self, mock_time, mock_sleep, mock_logger, mock_exception):
        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()
        self._db_manager._connect_tenants = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err'),
            None]

        self._db_manager.start(
            '10.10.10.10', 30013, 'user', 'pass', multi_tenant=False, timeout=2)

        self._db_manager._system_db_connector.connect.assert_has_calls([
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE'),
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE'),
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE')
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
        mock_exception.ConnectionError = Exception
        mock_time.side_effect = [0, 1, 2, 3]
        self._db_manager._system_db_connector = mock.Mock()
        self._db_manager._connect_tenants = mock.Mock()

        self._db_manager._system_db_connector.connect.side_effect = [
            mock_exception.ConnectionError('err'),
            mock_exception.ConnectionError('err'),
            None]

        self._db_manager.start(
            '10.10.10.10', 30013, 'user', 'pass', multi_tenant=True, timeout=2)

        self._db_manager._system_db_connector.connect.assert_has_calls([
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE'),
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE'),
            mock.call('10.10.10.10', 30013, user='user', password='pass', RECONNECT='FALSE')
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
        self._db_manager._connect_tenants.assert_called_once_with('10.10.10.10', 'user', 'pass')


    def test_get_connectors(self):
        self._db_manager._db_connectors = 'conns'
        assert 'conns' == self._db_manager.get_connectors()
