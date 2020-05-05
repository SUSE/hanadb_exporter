"""
Unitary tests for exporters/prometheus_exporter.py.

:author: abelarbi
:organization: SUSE Linux GmbH
:contact: abelarbi@suse.de

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

from hanadb_exporter import prometheus_exporter

class TestSapHanaCollectors(object):
    """
    Unitary tests for SapHanaCollectors.
    """

    @mock.patch('hanadb_exporter.prometheus_exporter.SapHanaCollector')
    def test_init(self, mock_collector):

        conn1 = mock.Mock()
        conn2 = mock.Mock()

        connectors = [conn1, conn2]

        coll1 = mock.Mock()
        coll2 = mock.Mock()
        mock_collector.side_effect = [coll1, coll2]

        collectors = prometheus_exporter.SapHanaCollectors(connectors, 'metrics.json')

        mock_collector.assert_has_calls([
            mock.call(conn1, 'metrics.json'),
            mock.call(conn2, 'metrics.json')
        ])

        assert collectors._collectors == [coll1, coll2]

    @mock.patch('hanadb_exporter.prometheus_exporter.SapHanaCollector')
    def test_collect(self, mock_collector):

        conn1 = mock.Mock()
        conn2 = mock.Mock()

        connectors = [conn1, conn2]

        metrics = ['metric1', 'metric2', 'metric3', 'metric4']
        coll1 = mock.Mock()
        coll1.collect.return_value=[metrics[0], metrics[1]]
        coll2 = mock.Mock()
        coll2.collect.return_value=[metrics[2], metrics[3]]

        mock_collector.side_effect = [coll1, coll2]

        collectors = prometheus_exporter.SapHanaCollectors(connectors, 'metrics.json')

        for i, metric in enumerate(collectors.collect()):
            assert metric == metrics[i]

        coll1.collect.assert_called_once_with()
        coll2.collect.assert_called_once_with()


class TestSapHanaCollector(object):
    """
    Unitary tests for SapHanaCollector.
    """

    @mock.patch('hanadb_exporter.prometheus_exporter.SapHanaCollector.retrieve_metadata')
    @mock.patch('hanadb_exporter.prometheus_metrics.PrometheusMetrics')
    def setup(self, mock_metrics, mock_retrieve_metadata):
        """
        Test setUp.
        """
        self._mock_metrics_config = mock.Mock()
        mock_metrics.return_value = self._mock_metrics_config
        self._mock_connector = mock.Mock()
        self._collector = prometheus_exporter.SapHanaCollector(self._mock_connector, 'metrics.json')

        self._collector._sid = 'prd'
        self._collector._insnr = '00'
        self._collector._database_name = 'db_name'
        self._collector._hana_version = '2.0'

        mock_retrieve_metadata.assert_called_once_with()

    def test_metadata_labels(self):
        assert ['prd', '00', 'db_name'] == self._collector.metadata_labels

    @mock.patch('hanadb_exporter.utils.format_query_result')
    @mock.patch('logging.Logger.info')
    def test_retrieve_metadata(self, mock_logger, mock_format_query):

        mock_result = mock.Mock()
        self._collector._hdb_connector.query = mock.Mock(return_value=mock_result)
        mock_format_query.return_value = [
            {'SID': 'ha1', 'INSNR': '10', 'DATABASE_NAME': 'DB_SYSTEM', 'VERSION': '1.2.3'}]

        self._collector.retrieve_metadata()

        mock_logger.assert_has_calls([
            mock.call('Querying database metadata...'),
            mock.call(
                'Metadata retrieved. version: %s, sid: %s, insnr: %s, database: %s',
                '1.2.3', 'ha1', '10', 'DB_SYSTEM')
        ])
        self._collector._hdb_connector.query.assert_called_once_with(
"""SELECT
(SELECT value
FROM M_SYSTEM_OVERVIEW
WHERE section = 'System'
AND name = 'Instance ID') SID,
(SELECT value
FROM M_SYSTEM_OVERVIEW
WHERE section = 'System'
AND name = 'Instance Number') INSNR,
m.database_name,
m.version
FROM m_database m;"""
        )
        mock_format_query.assert_called_once_with(mock_result)
        assert self._collector._sid == 'ha1'
        assert self._collector._insnr == '10'
        assert self._collector._database_name == 'DB_SYSTEM'
        assert self._collector._hana_version == '1.2.3'

    @mock.patch('hanadb_exporter.prometheus_exporter.core')
    @mock.patch('logging.Logger.debug')
    def test_manage_gauge(self, mock_logger, mock_core):

        mock_gauge_instance = mock.Mock()
        mock_gauge_instance.samples = 'samples'
        mock_core.GaugeMetricFamily = mock.Mock()
        mock_core.GaugeMetricFamily.return_value = mock_gauge_instance

        mock_metric = mock.Mock()
        mock_metric.name = 'name'
        mock_metric.description = 'description'
        mock_metric.labels = ['column1', 'column2']
        mock_metric.unit = 'mb'
        mock_metric.value = 'column3'

        formatted_query = [
            {'column1':'data1', 'column2':'data2', 'column3':'data3'},
            {'column1':'data4', 'column2':'data5', 'column3':'data6'},
            {'column1':'data7', 'column2':'data8', 'column3':'data9'}
        ]

        metric_obj = self._collector._manage_gauge(mock_metric, formatted_query)

        mock_core.GaugeMetricFamily.assert_called_once_with(
            'name', 'description', None,
            ['sid', 'insnr', 'database_name', 'column1', 'column2'], 'mb')

        mock_gauge_instance.add_metric.assert_has_calls([
            mock.call(['prd', '00', 'db_name', 'data1', 'data2'], 'data3'),
            mock.call(['prd', '00', 'db_name', 'data4', 'data5'], 'data6'),
            mock.call(['prd', '00', 'db_name', 'data7', 'data8'], 'data9')
        ])

        mock_logger.assert_called_once_with('%s \n', 'samples')
        assert metric_obj == mock_gauge_instance

    @mock.patch('hanadb_exporter.prometheus_exporter.core')
    @mock.patch('logging.Logger.warn')
    @mock.patch('logging.Logger.debug')
    def test_manage_gauge_incorrect_label(self, logger_debug, logger_warn, mock_core):

        mock_gauge_instance = mock.Mock()
        mock_gauge_instance.samples = []
        mock_core.GaugeMetricFamily = mock.Mock()
        mock_core.GaugeMetricFamily.return_value = mock_gauge_instance

        mock_metric = mock.Mock()
        mock_metric.name = 'name'
        mock_metric.description = 'description'
        mock_metric.labels = ['column4', 'column5']
        mock_metric.unit = 'mb'
        mock_metric.value = 'column3'

        formatted_query = [
            {'column1': 'data1', 'column2': 'data2', 'column3': 'data3'}
        ]

        metric_obj = self._collector._manage_gauge(mock_metric, formatted_query)

        mock_core.GaugeMetricFamily.assert_called_once_with(
            'name', 'description', None,
            ['sid', 'insnr', 'database_name', 'column4', 'column5'], 'mb')

        logger_warn.assert_called_once_with(
            'One or more label(s) specified in metrics.json '
            'for metric "%s" that are not found in the query result',
            'name')

        assert mock_gauge_instance.call_count == 0
        logger_debug.assert_called_once_with('%s \n', [])

    @mock.patch('hanadb_exporter.prometheus_exporter.core')
    @mock.patch('logging.Logger.warn')
    @mock.patch('logging.Logger.debug')
    def test_manage_gauge_incorrect_value(self, logger_debug, logger_warn, mock_core):

        mock_gauge_instance = mock.Mock()
        mock_gauge_instance.samples = []
        mock_core.GaugeMetricFamily = mock.Mock()
        mock_core.GaugeMetricFamily.return_value = mock_gauge_instance

        mock_metric = mock.Mock()
        mock_metric.name = 'name'
        mock_metric.description = 'description'
        mock_metric.labels = ['column1', 'column2']
        mock_metric.unit = 'mb'
        mock_metric.value = 'column4'

        formatted_query = [
            {'column1': 'data1', 'column2': 'data2', 'column3': 'data3'},
            {'column1': 'data4', 'column4': None, 'column3': 'data6'}
        ]

        metric_obj = self._collector._manage_gauge(mock_metric, formatted_query)

        mock_core.GaugeMetricFamily.assert_called_once_with(
            'name', 'description', None,
            ['sid', 'insnr', 'database_name', 'column1', 'column2'], 'mb')

        logger_warn.assert_has_calls([
            mock.call(
                'Specified value in metrics.json for metric "%s": (%s) not found or it is '\
                'invalid (None) in the query result',
                'name', 'column4'),
            mock.call(
                'Specified value in metrics.json for metric "%s": (%s) not found or it is '\
                'invalid (None) in the query result',
                'name', 'column4')
        ])
        assert mock_gauge_instance.call_count == 0
        logger_debug.assert_called_once_with('%s \n', [])

    def test_reconnect_connected(self):
        self._mock_connector.isconnected.return_value = True
        self._collector.reconnect()
        self._mock_connector.isconnected.assert_called_once_with()
        self._mock_connector.reconnect.assert_not_called()

    def test_reconnect_not_connected(self):
        self._mock_connector.isconnected.return_value = False
        self._collector.retrieve_metadata = mock.Mock()
        self._collector.reconnect()
        self._mock_connector.isconnected.assert_called_once_with()
        self._mock_connector.reconnect.assert_called_once_with()
        self._collector.retrieve_metadata.assert_called_once_with()

    @mock.patch('hanadb_exporter.utils.format_query_result')
    @mock.patch('hanadb_exporter.utils.check_hana_range')
    @mock.patch('logging.Logger.error')
    def test_collect_value_error(self, mock_logger, mock_hana_range, mock_format_query):
        """
        Test that when _manage_gauge is called and return ValueError (labels or value)
        are incorrect, that the ValueError is catched by collect() and a error is raised
        """
        self._collector.reconnect = mock.Mock()
        self._collector._manage_gauge = mock.Mock()

        self._collector._manage_gauge.side_effect = ValueError('test')
        mock_hana_range.return_value = True

        metrics1_1 = mock.Mock(type='gauge')
        metrics1 = [metrics1_1]
        query1 = mock.Mock(enabled=True, query='query1', metrics=metrics1, hana_version_range=['1.0'])

        self._collector._metrics_config.queries = [query1]

        for _ in self._collector.collect():
            continue

        self._collector.reconnect.assert_called_once_with()
        mock_logger.assert_called_once_with('test')

    @mock.patch('hanadb_exporter.utils.format_query_result')
    @mock.patch('hanadb_exporter.utils.check_hana_range')
    @mock.patch('logging.Logger.warning')
    @mock.patch('logging.Logger.info')
    def test_collect(self, mock_logger, mock_logger_warning, mock_hana_range, mock_format_query):

        self._collector.reconnect = mock.Mock()
        self._collector._manage_gauge = mock.Mock()

        self._mock_connector.query.side_effect = [
            'result1', 'result2', '']
        mock_format_query.side_effect = [
            'form_result1', 'form_result2', '']

        mock_hana_range.side_effect = [True, True, False, True]

        self._collector._manage_gauge.side_effect = [
            'gauge1', 'gauge2', 'gauge3', 'gauge4', 'gauge5']

        metrics1_1 = mock.Mock(type='gauge')
        metrics1_2 = mock.Mock(type='gauge')
        metrics1 = [metrics1_1, metrics1_2]
        query1 = mock.Mock(enabled=True, query='query1', metrics=metrics1, hana_version_range=['1.0'])
        metrics2_1 = mock.Mock(type='gauge')
        metrics2_2 = mock.Mock(type='gauge')
        metrics2 = [metrics2_1, metrics2_2]
        query2 = mock.Mock(enabled=False, query='query2', metrics=metrics2, hana_version_range=['2.0'])
        metrics3_1 = mock.Mock(type='gauge')
        metrics3_2 = mock.Mock(type='gauge')
        metrics3_3 = mock.Mock(type='gauge')
        metrics3 = [metrics3_1, metrics3_2, metrics3_3]
        query3 = mock.Mock(enabled=True, query='query3', metrics=metrics3, hana_version_range=['3.0'])
        metrics4_1 = mock.Mock(type='gauge')
        metrics4_2 = mock.Mock(type='gauge')
        metrics4 = [metrics2_1, metrics2_2]
        query4 = mock.Mock(enabled=True, query='query4', metrics=metrics4, hana_version_range=['1.0.0', '2.0.0'])
        query5 = mock.Mock(enabled=True, query='query5', metrics=[], hana_version_range=['4.0'])

        self._collector._metrics_config.queries = [
            query1, query2, query3, query4, query5
        ]

        for index, element in enumerate(self._collector.collect()):
            assert element == 'gauge{}'.format(index+1)

        self._collector.reconnect.assert_called_once_with()
        self._mock_connector.query.assert_has_calls([
            mock.call('query1'),
            mock.call('query3'),
            mock.call('query5')])

        mock_format_query.assert_has_calls([
            mock.call('result1'),
            mock.call('result2'),
            mock.call('')
        ])

        mock_hana_range.assert_has_calls([
            mock.call('2.0', ['1.0']),
            mock.call('2.0', ['3.0']),
            mock.call('2.0', ['1.0.0', '2.0.0']),
            mock.call('2.0', ['4.0'])
        ])

        self._collector._manage_gauge.assert_has_calls([
            mock.call(metrics1_1, 'form_result1'),
            mock.call(metrics1_2, 'form_result1'),
            mock.call(metrics3_1, 'form_result2'),
            mock.call(metrics3_2, 'form_result2'),
            mock.call(metrics3_3, 'form_result2'),
        ])

        mock_logger.assert_has_calls([
            mock.call('Query %s is disabled', 'query2'),
            mock.call('Query %s out of the provided hana version range: %s',
                'query4', ['1.0.0', '2.0.0'])
        ])

        mock_logger_warning.assert_called_once_with(
            'Query %s ... has not returned any record', 'query5')

    @mock.patch('hanadb_exporter.utils.format_query_result')
    @mock.patch('hanadb_exporter.utils.check_hana_range')
    def test_collect_incorrect_type(self, mock_hana_range, mock_format_query):

        self._collector.reconnect = mock.Mock()
        self._collector._manage_gauge = mock.Mock()

        self._mock_connector.query.side_effect = [
            'result1', 'result2']
        mock_format_query.side_effect = [
            'form_result1', 'form_result2']

        mock_hana_range.side_effect = [True, True, True]

        self._collector._manage_gauge.side_effect = [
            'gauge1', 'gauge2', 'gauge3', 'gauge4', 'gauge5']

        metrics1_1 = mock.Mock(type='gauge')
        metrics1_2 = mock.Mock(type='gauge')
        metrics1 = [metrics1_1, metrics1_2]
        query1 = mock.Mock(enabled=True, query='query1', metrics=metrics1, hana_version_range=['1.0'])
        metrics2_1 = mock.Mock(type='gauge')
        metrics2_2 = mock.Mock(type='gauge')
        metrics2 = [metrics2_1, metrics2_2]
        query2 = mock.Mock(enabled=False, query='query2', metrics=metrics2, hana_version_range=['2.0'])
        metrics3_1 = mock.Mock(type='gauge')
        metrics3_2 = mock.Mock(type='other')
        metrics3_3 = mock.Mock(type='gauge')
        metrics3 = [metrics3_1, metrics3_2, metrics3_3]
        query3 = mock.Mock(enabled=True, query='query3', metrics=metrics3, hana_version_range=['3.0'])

        self._collector._metrics_config.queries = [
            query1, query2, query3
        ]

        with pytest.raises(NotImplementedError) as err:
            for index, element in enumerate(self._collector.collect()):
                assert element == 'gauge{}'.format(index+1)

        self._collector.reconnect.assert_called_once_with()
        assert '{} type not implemented'.format('other') in str(err.value)

        self._mock_connector.query.assert_has_calls([
            mock.call('query1'),
            mock.call('query3')])

        mock_format_query.assert_has_calls([
            mock.call('result1'),
            mock.call('result2')
        ])

        mock_hana_range.assert_has_calls([
            mock.call('2.0', ['1.0']),
            mock.call('2.0', ['3.0'])
        ])

        self._collector._manage_gauge.assert_has_calls([
            mock.call(metrics1_1, 'form_result1'),
            mock.call(metrics1_2, 'form_result1'),
            mock.call(metrics3_1, 'form_result2')
        ])

    @mock.patch('hanadb_exporter.utils.check_hana_range')
    @mock.patch('hanadb_exporter.prometheus_exporter.hdb_connector.connectors.base_connector')
    @mock.patch('logging.Logger.error')
    def test_collect_incorrect_query(self, mock_logger, mock_base_connector, mock_hana_range):

        self._collector.reconnect = mock.Mock()
        mock_base_connector.QueryError = Exception

        self._mock_connector.query.side_effect = Exception('error')
        mock_hana_range.return_value = True

        query1 = mock.Mock(enabled=True, query='query1', hana_version_range=['1.0'])

        self._collector._metrics_config.queries = [query1]

        for _ in self._collector.collect():
            continue

        self._collector.reconnect.assert_called_once_with()
        self._mock_connector.query.assert_called_once_with('query1')

        mock_hana_range.assert_has_calls([
            mock.call('2.0', ['1.0']),
        ])

        mock_logger.assert_has_calls([
            mock.call('Failure in query: %s, skipping...', 'query1'),
        ])
