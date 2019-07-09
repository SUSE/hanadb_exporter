"""
Unitary tests for hanadb_exporter/exporter_factory.py.

:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2019-06-12
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

from hanadb_exporter import exporter_factory


class TestSapHanaExporter(object):
    """
    Unitary tests for hanadb_exporter/exporter_factory.py.
    """

    @mock.patch('hanadb_exporter.utils.format_query_result')
    def test_get_hana_version(self, mock_format_query):
        mock_connector = mock.Mock()
        mock_connector.query.return_value = 'query_result'
        mock_format_query.return_value = [{'VERSION': '2.0'}]
        version = exporter_factory.SapHanaExporter.get_hana_version(mock_connector)

        mock_connector.query.assert_called_once_with('SELECT * FROM sys.m_database;')
        mock_format_query.assert_called_once_with('query_result')
        assert version == '2.0'

    @mock.patch('hanadb_exporter.exporters.prometheus_exporter.SapHanaCollector')
    @mock.patch('hanadb_exporter.exporter_factory.SapHanaExporter.get_hana_version')
    @mock.patch('logging.Logger.info')
    def test_create(self, mock_logger, mock_get_hana, mock_hana_collector):
        mocked_collector = mock.Mock()
        mock_connector = mock.Mock()
        mock_hana_collector.return_value = mocked_collector
        mock_get_hana.return_value = '2.0'
        collector = exporter_factory.SapHanaExporter.create(
            exporter_type='prometheus', hdb_connector=mock_connector, metrics_file='metrics.json')

        mock_get_hana.assert_called_once_with(mock_connector)
        mock_hana_collector.assert_called_once_with(
            connector=mock_connector,
            metrics_file='metrics.json',
            hana_version='2.0')
        mock_logger.assert_has_calls([
            mock.call('SAP HANA database version: %s', '2.0'),
            mock.call('prometheus exporter selected')
        ])
        assert collector == mocked_collector

    @mock.patch('hanadb_exporter.exporter_factory.SapHanaExporter.get_hana_version')
    def test_create_error(self, mock_get_hana):
        mock_connector = mock.Mock()
        with pytest.raises(NotImplementedError) as err:
            exporter_factory.SapHanaExporter.create(
                exporter_type='other', hdb_connector=mock_connector, metrics_file='metrics.json')

        mock_get_hana.assert_called_once_with(mock_connector)
        assert '{} exporter not implemented'.format('other') in str(err.value)
