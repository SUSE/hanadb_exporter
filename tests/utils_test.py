"""
Unitary tests for utils.py.

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.com

:since: 2019-07-05
"""

# pylint:disable=C0103,C0111,W0212,W0611

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

sys.modules['prometheus_client'] = mock.MagicMock()

from hanadb_exporter import utils


class TestUtils(object):
    """
    Unitary tests for utils.
    """


    def test_format_query_result(self):
        query_results = mock.Mock()
        query_results.metadata = [
            ('column1', 'other_data',), ('column2', 'other_data'), ('column3', 'other_data')]
        query_results.records = [
            ('data1', 'data2', 'data3'),
            ('data4', 'data5', 'data6'),
            ('data7', 'data8', 'data9')
        ]
        formatted_result = utils.format_query_result(query_results)

        assert formatted_result == [
            {'column1':'data1', 'column2':'data2', 'column3':'data3'},
            {'column1':'data4', 'column2':'data5', 'column3':'data6'},
            {'column1':'data7', 'column2':'data8', 'column3':'data9'}
        ]

    def test_check_hana_range(self):

        assert utils.check_hana_range('1.0.0.0', ['1.0.0.1']) == False
        assert utils.check_hana_range('1.0.0.0', ['1.0.0']) == True
        assert utils.check_hana_range('1.0.0.0', ['1.0.0']) == True
        assert utils.check_hana_range('1.0.0.1', ['1.0.0.0']) == True

        assert utils.check_hana_range('1.0.0.0', ['1.0.0.1', '2.0.0']) == False
        assert utils.check_hana_range('2.0.1.0', ['1.0.0.1', '2.0.0.0']) == False
        assert utils.check_hana_range('1.0.0.0', ['1.0.1.0', '2.0.0.0']) == False
        assert utils.check_hana_range('1.0.1.0', ['1.0.1.1', '2.0.0.0']) == False
        assert utils.check_hana_range('1.0.0.1', ['1.0.1', '2.0.0.0']) == False

        assert utils.check_hana_range('1.0.0.0', ['1.0.0', '2.0.0']) == True
        assert utils.check_hana_range('1.0.1', ['1.0.0.1', '2.0.0']) == True
        assert utils.check_hana_range('1.0.1', ['1.0.0.0', '2.0.0']) == True
        assert utils.check_hana_range('2.0.0.0', ['1.0.0.1', '2.0.0.0']) == True
        assert utils.check_hana_range('1.0.0.1', ['1.0.0', '2.0.0.0']) == True

        with pytest.raises(ValueError) as err:
            utils.check_hana_range('1.0.0.0', [])

        assert 'provided availability range does not have the correct number of elements' in str(err.value)

        with pytest.raises(ValueError) as err:
            utils.check_hana_range('1.0.0.0', ['1.0.0.0', '2.0.0.0', '3.0.0.0'])

        assert 'provided availability range does not have the correct number of elements' in str(err.value)

    @mock.patch('os.getenv')
    @mock.patch('socket.socket')
    def test_systemd_ready_error(self, mock_socket, mock_getenv):
        mock_getenv.return_value = None
        with pytest.raises(utils.NotSystemdException) as err:
            utils.systemd_ready()

        assert 'Exporter is not running as systemd deamon' in str(err.value)

    @mock.patch('os.getenv')
    @mock.patch('socket.socket')
    def test_systemd_ready(self, mock_socket, mock_getenv):
        mock_getenv.return_value = '@notify'
        sock_instance = mock.Mock()
        mock_socket.return_value = sock_instance
        utils.systemd_ready()

        sock_instance.connect.assert_called_once_with('\0notify')
        sock_instance.sendall.assert_called_once_with(b'READY=1')
