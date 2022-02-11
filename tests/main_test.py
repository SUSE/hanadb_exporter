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

from hanadb_exporter import __version__
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
                "-c", "--config", help="Path to hanadb_exporter configuration file"),
            mock.call(
                "-m", "--metrics", help="Path to hanadb_exporter metrics file"),
            mock.call(
                "-d", "--daemon", action="store_true", help="Start the exporter as a systemd daemon. Only used when the the application "\
                     "is managed by systemd"),
            mock.call(
                "--identifier",
                help="Identifier of the configuration file from /etc/hanadb_exporter"),
            mock.call(
                "-v", "--verbosity",
                help="Python logging level. Options: DEBUG, INFO, WARN, ERROR (INFO by default)"),
            mock.call(
                "-V", "--version", action="store_true",
                help="Print the hanadb_exporter version")
        ])

        mocked_parser.parse_args.assert_called_once_with()

        assert parsed_arguments == 'parsed_arguments'

    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('builtins.print')
    def test_version(self, mock_print, mock_parse_arguments):
        mock_arguments = mock.Mock(version=True)
        mock_parse_arguments.return_value = mock_arguments
        main.run()
        mock_print.assert_called_once_with('hanadb_exporter %s' % (__version__))

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

    @mock.patch('os.path.isfile')
    def test_lookup_etc_folder(self, mock_isfile):
        mock_isfile.return_value = True
        metric_file = main.lookup_etc_folder(main.METRICS_FILES)
        assert metric_file == main.METRICS_FILES[0]

    @mock.patch('os.path.isfile')
    def test_lookup_etc_folder_error(self, mock_isfile):
        mock_isfile.side_effect = [False, False]
        with pytest.raises(ValueError) as err:
            main.lookup_etc_folder(main.METRICS_FILES)
        assert 'configuration file does not exist in {}'.format(",".join(main.METRICS_FILES)) in str(err.value)

    @mock.patch('hanadb_exporter.utils.systemd_ready')
    @mock.patch('hanadb_exporter.main.LOGGER')
    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('hanadb_exporter.main.parse_config')
    @mock.patch('hanadb_exporter.main.setup_logging')
    @mock.patch('hanadb_exporter.main.db_manager.DatabaseManager')
    @mock.patch('hanadb_exporter.main.prometheus_exporter.SapHanaCollectors')
    @mock.patch('hanadb_exporter.main.REGISTRY.register')
    @mock.patch('hanadb_exporter.main.start_http_server')
    @mock.patch('logging.getLogger')
    @mock.patch('time.sleep')
    def test_run(
            self, mock_sleep, mock_get_logger, mock_start_server, mock_registry,
            mock_exporters, mock_db_manager, mock_setup_logging,
            mock_parse_config, mock_parse_arguments, mock_logger, mock_systemd):

        mock_arguments = mock.Mock(config='config', metrics='metrics', daemon=False, version=False)
        mock_parse_arguments.return_value = mock_arguments

        config = {
            'listen_address': '127.0.0.1',
            'hana': {
                'host': '10.10.10.10',
                'port': 1234,
                'user': 'user',
                'password': 'pass',
                'ssl': True,
                'ssl_validate_cert': True
            },
            'logging': {
                'log_file': 'my_file',
                'config_file': 'my_config_file'
            }
        }
        mock_parse_config.return_value = config

        db_instance = mock.Mock()
        db_instance.get_connectors.return_value = 'connectors'
        mock_db_manager.return_value = db_instance

        mock_collector = mock.Mock()
        mock_exporters.return_value = mock_collector

        mock_sleep.side_effect = Exception

        with pytest.raises(Exception):
            main.run()

        mock_parse_arguments.assert_called_once_with()
        mock_parse_config.assert_called_once_with(mock_arguments.config)
        mock_setup_logging.assert_called_once_with(config)
        mock_db_manager.assert_called_once_with()
        db_instance.start.assert_called_once_with(
            '10.10.10.10', 1234, user='user', password='pass',
            userkey=None, multi_tenant=True, timeout=30, ssl=True, ssl_validate_cert=True)
        db_instance.get_connectors.assert_called_once_with()
        mock_exporters.assert_called_once_with(
            connectors='connectors', metrics_file='metrics')

        mock_registry.assert_called_once_with(mock_collector)
        mock_logger.info.assert_has_calls([
            mock.call('exporter successfully registered'),
            mock.call('starting to serve metrics')
        ])
        mock_start_server.assert_called_once_with(9668, '127.0.0.1')
        mock_sleep.assert_called_once_with(1)
        assert mock_systemd.call_count == 0

    @mock.patch('hanadb_exporter.utils.systemd_ready')
    @mock.patch('hanadb_exporter.main.LOGGER')
    @mock.patch('hanadb_exporter.main.lookup_etc_folder')
    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('hanadb_exporter.main.parse_config')
    @mock.patch('hanadb_exporter.main.setup_logging')
    @mock.patch('hanadb_exporter.main.db_manager.DatabaseManager')
    @mock.patch('hanadb_exporter.main.prometheus_exporter.SapHanaCollectors')
    @mock.patch('hanadb_exporter.main.REGISTRY.register')
    @mock.patch('hanadb_exporter.main.start_http_server')
    @mock.patch('logging.getLogger')
    @mock.patch('time.sleep')
    def test_run_defaults(
            self, mock_sleep, mock_get_logger, mock_start_server, mock_registry,
            mock_exporters, mock_db_manager, mock_setup_logging, mock_parse_config,
            mock_parse_arguments, mock_lookup_etc_folder, mock_logger, mock_systemd):

        mock_arguments = mock.Mock(
            config=None, metrics=None, identifier='config', daemon=True, version=False)
        mock_parse_arguments.return_value = mock_arguments

        mock_lookup_etc_folder.return_value = 'new_metrics'

        config = {
            'hana': {
                'host': '10.10.10.10',
                'port': 1234,
                'user': 'user',
                'password': 'pass'
            },
            'logging': {
                'log_file': 'my_file',
                'config_file': 'my_config_file'
            }
        }
        mock_parse_config.return_value = config

        db_instance = mock.Mock()
        db_instance.get_connectors.return_value = 'connectors'
        mock_db_manager.return_value = db_instance

        mock_collector = mock.Mock()
        mock_exporters.return_value = mock_collector

        mock_sleep.side_effect = Exception

        with pytest.raises(Exception):
            main.run()

        mock_parse_arguments.assert_called_once_with()
        mock_parse_config.assert_called_once_with("new_metrics")
        mock_setup_logging.assert_called_once_with(config)
        mock_db_manager.assert_called_once_with()
        db_instance.start.assert_called_once_with(
            '10.10.10.10', 1234, user='user', password='pass',
            userkey=None, multi_tenant=True, timeout=30, ssl=False, ssl_validate_cert=False)
        db_instance.get_connectors.assert_called_once_with()
        mock_exporters.assert_called_once_with(
            connectors='connectors', metrics_file='new_metrics')

        mock_registry.assert_called_once_with(mock_collector)
        mock_logger.info.assert_has_calls([
            mock.call('exporter successfully registered'),
            mock.call('starting to serve metrics')
        ])
        mock_start_server.assert_called_once_with(9668, '0.0.0.0')
        mock_sleep.assert_called_once_with(1)
        mock_systemd.assert_called_once_with()

    @mock.patch('hanadb_exporter.main.parse_arguments')
    def test_run_invalid_args(self, mock_parse_arguments):

        mock_arguments = mock.Mock(config=None, identifier=None, version=False)
        mock_parse_arguments.return_value = mock_arguments

        with pytest.raises(ValueError) as err:
            main.run()

        assert 'configuration file or identifier must be used' in str(err.value)

    @mock.patch('hanadb_exporter.main.LOGGER')
    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('hanadb_exporter.main.parse_config')
    @mock.patch('hanadb_exporter.main.db_manager.DatabaseManager')
    @mock.patch('logging.getLogger')
    @mock.patch('logging.basicConfig')
    def test_run_malformed(
            self, mock_logging, mock_get_logger, mock_db_manager,
            mock_parse_config, mock_parse_arguments, mock_logger):

        mock_arguments = mock.Mock(
            config='config', metrics='metrics', verbosity='DEBUG', version=False)
        mock_parse_arguments.return_value = mock_arguments

        config = {
            'hana': {
                'port': 1234,
                'user': 'user',
                'password': 'pass'
            }
        }
        mock_parse_config.return_value = config

        with pytest.raises(KeyError) as err:
            main.run()

        mock_parse_arguments.assert_called_once_with()
        mock_parse_config.assert_called_once_with(mock_arguments.config)
        mock_logging.assert_called_once_with(level='DEBUG')
        mock_db_manager.assert_called_once_with()
        assert 'Configuration file {} is malformed: {} not found'.format(
            'config', '\'host\'') in str(err.value)

    @mock.patch('hanadb_exporter.utils.systemd_ready')
    @mock.patch('hanadb_exporter.main.LOGGER')
    @mock.patch('hanadb_exporter.main.parse_arguments')
    @mock.patch('hanadb_exporter.main.parse_config')
    @mock.patch('hanadb_exporter.main.setup_logging')
    @mock.patch('hanadb_exporter.main.db_manager.DatabaseManager')
    @mock.patch('hanadb_exporter.main.prometheus_exporter.SapHanaCollectors')
    @mock.patch('hanadb_exporter.main.REGISTRY.register')
    @mock.patch('hanadb_exporter.main.start_http_server')
    @mock.patch('logging.getLogger')
    @mock.patch('time.sleep')
    @mock.patch('hanadb_exporter.main.secrets_manager.get_db_credentials')
    def test_run_secret_manager(
            self, mock_secret_manager, mock_sleep, mock_get_logger, mock_start_server, mock_registry,
            mock_exporters, mock_db_manager, mock_setup_logging,
            mock_parse_config, mock_parse_arguments, mock_logger, mock_systemd):

        mock_arguments = mock.Mock(config='config', metrics='metrics', daemon=False, version=False)
        mock_parse_arguments.return_value = mock_arguments
        mock_secret_manager.return_value = {
            'username': 'db_user',
            'password': 'db_pass'
        }

        config = {
            'hana': {
                'host': '10.10.10.10',
                'port': 1234,
                'aws_secret_name': 'db_secret',
                'user': 'user',
                'password': 'pass'
            },
            'logging': {
                'log_file': 'my_file',
                'config_file': 'my_config_file'
            }
        }

        mock_parse_config.return_value = config

        db_instance = mock.Mock()
        db_instance.get_connectors.return_value = 'connectors'
        mock_db_manager.return_value = db_instance

        mock_collector = mock.Mock()
        mock_exporters.return_value = mock_collector

        mock_sleep.side_effect = Exception

        with pytest.raises(Exception):
            main.run()

        mock_parse_arguments.assert_called_once_with()
        mock_parse_config.assert_called_once_with(mock_arguments.config)
        mock_setup_logging.assert_called_once_with(config)
        mock_db_manager.assert_called_once_with()
        db_instance.start.assert_called_once_with(
            '10.10.10.10', 1234, user='db_user', password='db_pass',
            userkey=None, multi_tenant=True, timeout=30, ssl=False, ssl_validate_cert=False)
        db_instance.get_connectors.assert_called_once_with()
        mock_exporters.assert_called_once_with(
            connectors='connectors', metrics_file='metrics')

        mock_registry.assert_called_once_with(mock_collector)
        mock_logger.info.assert_has_calls([
            mock.call('AWS secret name is going to be used to read the database username and password'),
            mock.call('exporter successfully registered'),
            mock.call('starting to serve metrics')
        ])
        mock_start_server.assert_called_once_with(9668, '0.0.0.0')
        mock_sleep.assert_called_once_with(1)
        assert mock_systemd.call_count == 0
