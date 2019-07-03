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

    @mock.patch('hanadb_exporter.exporters.prometheus_exporter.SapHanaCollector')
    @mock.patch('logging.Logger.info')
    def test_create(self, mock_logger, mock_hana_collector):
        mocked_collector = mock.Mock()
        mock_connector = mock.Mock()
        mock_hana_collector.return_value = mocked_collector
        collector = exporter_factory.SapHanaExporter.create(
            exporter_type='prometheus', hdb_connector=mock_connector, metrics_file='metrics.json')

        mock_logger.assert_called_once_with('prometheus exporter selected')
        assert collector == mocked_collector

    def test_create_error(self):
        mock_connector = mock.Mock()
        with pytest.raises(NotImplementedError) as err:
            exporter_factory.SapHanaExporter.create(
                exporter_type='other', hdb_connector=mock_connector, metrics_file='metrics.json')

        assert '{} exporter not implemented'.format('other') in str(err.value)
