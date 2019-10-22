"""
Unitary tests for exporters/main.py.

:author: abelarbi, xarbulu
:organization: SUSE Linux GmbH
:contact: abelarbi@suse.de, xarbulu@suse.com

:since: 2019-06-11
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

sys.modules['shaptools'] = mock.MagicMock()
sys.modules['prometheus_client'] = mock.MagicMock()
sys.modules['prometheus_client.core'] = mock.MagicMock()

from hanadb_exporter import main


class TestMain(object):
    """
    Unitary tests for hanadb_exporter/main.py.
    """

    @mock.patch('json.load')
    @mock.patch('hanadb_exporter.main.open')
    def test_parse_config(self, mock_open, mock_load):
        main.parse_config('config.json')
        mock_open.assert_called_once_with('config.json', 'r')
        assert mock_load.call_count == 1

    @mock.patch('argparse.ArgumentParser')
    def test_parse_arguments(self, mock_parser):
        mocked_parser = mock.Mock()
        mock_parser.return_value = mocked_parser
        mocked_parser.parse_args.return_value = 'parsed_arguments'

        parsed_arguments = main.parse_arguments()

        mock_parser.assert_called_once_with()
        mocked_parser.add_argument.assert_has_calls([
            mock.call(
                "-c", "--config", help="Path to hanadb_exporter configuration file", required=True),
            mock.call(
                "-m", "--metrics", help="Path to hanadb_exporter metrics file", required=True),
            mock.call(
                "-v", "--verbosity",
                help="Python logging level. Options: DEBUG, INFO, WARN, ERROR (INFO by default)")
        ])

        mocked_parser.parse_args.assert_called_once_with()

        assert parsed_arguments == 'parsed_arguments'

    @mock.patch('hanadb_exporter.main.fileConfig')
    def test_setup_logging(self, mock_file_config):
        config = {
            'hana': {
                'host': '123.123.123.123',
                'port': 1234
            },
            'logging': {
                'log_file': 'my_file',
                'config_file': 'my_config_file'
            }
        }

        main.setup_logging(config)

        config['logging'].pop('log_file')
        main.setup_logging(config)

        mock_file_config.assert_has_calls([
            mock.call('my_config_file', defaults={'logfilename': 'my_file'}),
            mock.call('my_config_file', defaults={'logfilename': '/var/log/hanadb_exporter_123.123.123.123_1234'})
        ])

    def test_connect(self):

        mock_connector = mock.Mock()
        config = {
            'hana': {
                'host': '123.123.123.123',
                'port': 1234,
                'user': 'user',
                'password': 'pass'
            }
        }
        mock_logger = mock.Mock()

        main.connect(mock_connector, config, mock_logger)

        mock_logger.info.assert_called_once_with(
            'connecting to the hana database (%s:%s)', '123.123.123.123', 1234)
        mock_connector.connect.assert_called_once_with(
            '123.123.123.123', 1234, user='user', password='pass')

    @mock.patch('hanadb_exporter.main.hdb_connector.connectors.base_connector')
    @mock.patch('time.sleep')
    def test_connect_loop(self, mock_sleep, mock_connection_error):

        mock_exception = Exception
        mock_connection_error.ConnectionError = mock_exception
        mock_connector = mock.Mock()
        config = {
            'hana': {
                'host': '123.123.123.123',
                'user': 'user',
                'password': 'pass'
            }
        }
        mock_logger = mock.Mock()

        mock_connector.connect.side_effect = [mock_exception('err1'), mock_exception('err2'), True]

        main.connect(mock_connector, config, mock_logger)

        mock_logger.info.assert_called_once_with(
            'connecting to the hana database (%s:%s)', '123.123.123.123', 30015)
        mock_connector.connect.assert_has_calls([
            mock.call('123.123.123.123', 30015, user='user', password='pass'),
            mock.call('123.123.123.123', 30015, user='user', password='pass'),
            mock.call('123.123.123.123', 30015, user='user', password='pass')
        ])

        mock_logger.error.assert_has_calls([
            mock.call('the connection to the database failed. error message: %s', 'err1'),
            mock.call('the connection to the database failed. error message: %s', 'err2')
        ])

        mock_sleep.assert_has_calls([
            mock.call(15),
            mock.call(15)
        ])

    @mock.patch('hanadb_exporter.main.connect')
    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('hanadb_exporter.main.parse_config')
    @mock.patch('hanadb_exporter.main.setup_logging')
    @mock.patch('hanadb_exporter.main.hdb_connector.HdbConnector')
    @mock.patch('hanadb_exporter.main.exporter_factory.SapHanaExporter.create')
    @mock.patch('hanadb_exporter.main.REGISTRY.register')
    @mock.patch('hanadb_exporter.main.start_http_server')
    @mock.patch('logging.getLogger')
    @mock.patch('time.sleep')
    def test_run(
            self, mock_sleep, mock_get_logger, mock_start_server, mock_registry,
            mock_exporter, mock_hdb, mock_setup_loggin,
            mock_parse_config, mock_parse_arguments, mock_connect):

        mock_arguments = mock.Mock(config='config', metrics='metrics')
        mock_parse_arguments.return_value = mock_arguments

        config = {
            'logging': {
                'log_file': 'my_file',
                'config_file': 'my_config_file'
            }
        }
        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger
        mock_parse_config.return_value = config

        mock_connector = mock.Mock()
        mock_hdb.return_value = mock_connector

        mock_collector = mock.Mock()
        mock_exporter.return_value = mock_collector

        mock_sleep.side_effect = Exception

        with pytest.raises(Exception):
            main.run()

        mock_parse_arguments.assert_called_once_with()
        mock_parse_config.assert_called_once_with(mock_arguments.config)
        mock_setup_loggin.assert_called_once_with(config)
        mock_hdb.assert_called_once_with()
        mock_connect.assert_called_once_with(mock_connector, config, mock_logger)
        mock_exporter.assert_called_once_with(
            exporter_type='prometheus', metrics_file='metrics', hdb_connector=mock_connector)
        mock_registry.assert_called_once_with(mock_collector)
        mock_logger.info.assert_has_calls([
            mock.call('exporter sucessfully registered'),
            mock.call('starting to serve metrics')
        ])
        mock_start_server.assert_called_once_with(8001, '0.0.0.0')
        mock_sleep.assert_called_once_with(1)

    @mock.patch('hanadb_exporter.main.connect')
    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('hanadb_exporter.main.parse_config')
    @mock.patch('hanadb_exporter.main.hdb_connector.HdbConnector')
    @mock.patch('logging.getLogger')
    @mock.patch('logging.basicConfig')
    def test_run_malformed(
            self, mock_logging, mock_get_logger, mock_hdb,
            mock_parse_config, mock_parse_arguments, mock_connect):

        mock_arguments = mock.Mock(config='config', metrics='metrics', verbosity='DEBUG')
        mock_parse_arguments.return_value = mock_arguments

        config = {
            'hana': {
                'host': '123.123.123.123',
                'port': 1234,
                'user': 'user',
                'password': 'pass'
            }
        }
        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger
        mock_parse_config.return_value = config
        mock_connect.side_effect = KeyError('error')
        hdb_instance = mock.Mock()
        mock_hdb.return_value = hdb_instance

        with pytest.raises(KeyError) as err:
            main.run()

        mock_parse_arguments.assert_called_once_with()
        mock_parse_config.assert_called_once_with(mock_arguments.config)
        mock_logging.assert_called_once_with(level='DEBUG')
        mock_hdb.assert_called_once_with()
        mock_connect.assert_called_once_with(hdb_instance, config, mock_logger)
        assert 'Configuration file {} is malformed: {} not found'.format(
            'config', '\'error\'') in str(err.value)
