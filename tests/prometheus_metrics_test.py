"""
Unitary tests for exporters/prometheus_metrics.py.

:author: abelarbi, xarbulu
:organization: SUSE Linux GmbH
:contact: abelarbi@suse.de, xarbulu@suse.com

:since: 2019-06-11
"""

# pylint:disable=C0103,C0111,W0212,W0611

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from hanadb_exporter import prometheus_metrics

class TestMetric(object):
    """
    Unitary tests for Metric.
    """

    def test_metric_new(self):
        correct_data = {
            'name': 'name',
            'description': 'description',
            'labels': list(),
            'value': 'value',
            'unit': 'unit',
            'type': 'type'
        }
        modeled_metric = prometheus_metrics.Metric(**correct_data)
        assert modeled_metric.name == 'name'
        assert modeled_metric.description == 'description'
        assert modeled_metric.labels == list()
        assert modeled_metric.value == 'value'
        assert modeled_metric.unit == 'unit'
        assert modeled_metric.type == 'type'
        assert modeled_metric.enabled == True
        assert modeled_metric.hana_version_range == ['1.0.0']

        correct_data = {
            'name': 'name',
            'description': 'description',
            'labels': list(),
            'value': 'value',
            'unit': 'unit',
            'type': 'type',
            'enabled': False,
            'hana_version_range': ['1.0.0', '2.0.0']
        }

        modeled_metric = prometheus_metrics.Metric(**correct_data)
        assert modeled_metric.name == 'name'
        assert modeled_metric.description == 'description'
        assert modeled_metric.labels == list()
        assert modeled_metric.value == 'value'
        assert modeled_metric.unit == 'unit'
        assert modeled_metric.type == 'type'
        assert modeled_metric.enabled == False
        assert modeled_metric.hana_version_range == ['1.0.0', '2.0.0']

        missing_data = {
            'name': 'name',
            'description': 'description',
            'labels': list(),
            'value': 'value',
            'type': 'type',
            'enabled': False
        }
        with pytest.raises(TypeError) as err:
            modeled_metric = prometheus_metrics.Metric(**missing_data)

        incorrect_data = {
            'name': 'name',
            'descriptio': 'description',
            'labels': list(),
            'value': 'value',
            'unit': 'unit',
            'type': 'type',
            'enabled': False
        }
        with pytest.raises(TypeError) as err:
            modeled_metric = prometheus_metrics.Metric(**missing_data)

        additional_data = {
            'name': 'name',
            'description': 'description',
            'labels': list(),
            'value': 'value',
            'unit': 'unit',
            'type': 'type',
            'extra': False
        }
        with pytest.raises(TypeError) as err:
            modeled_metric = prometheus_metrics.Metric(**missing_data)

    def test_metric_new_error(self):
        correct_data = {
            'name': 'name',
            'description': 'description',
            'labels': list(),
            'value': '',
            'unit': 'unit',
            'type': 'type'
        }

        with pytest.raises(ValueError) as err:
            prometheus_metrics.Metric(**correct_data)

        assert 'No value specified in metrics.json for {}'.format('name') in str(err.value)

class TestQuery(object):
    """
    Unitary tests for Query.
    """

    def setup(self):
        self._query = prometheus_metrics.Query()

    @mock.patch('hanadb_exporter.prometheus_metrics.Metric')
    def test_parse(self, mock_metric):
        mocked_data1 = {'data1': 'value1'}
        mocked_data2 = {'data2': 'value2'}
        query_data = {'metrics': [mocked_data1, mocked_data2], 'enabled': False}
        mock_metric.side_effect = ['modeled_data1', 'modeled_data2']

        self._query.parse('query', query_data)

        mock_metric.assert_has_calls([
            mock.call(data1='value1'),
            mock.call(data2='value2')
        ])
        assert self._query.query == 'query'
        assert self._query.enabled == False
        assert self._query.metrics == ['modeled_data1', 'modeled_data2']

    @mock.patch('hanadb_exporter.prometheus_metrics.Query.__new__')
    def test_get_model(self, mock_query):
        mock_query_instance = mock.Mock()
        mock_query.return_value = mock_query_instance
        modeled_query = prometheus_metrics.Query.get_model('query', ['metric1', 'metric2'])
        mock_query_instance.parse.assert_called_once_with('query', ['metric1', 'metric2'])
        assert modeled_query == mock_query_instance


class TestPrometheusMetrics(object):
    """
    Unitary tests for PrometheusMetrics.
    """

    @mock.patch('hanadb_exporter.prometheus_metrics.PrometheusMetrics.load_metrics')
    def test_init(self, mock_load):
        mock_load.return_value = 'queries'
        metrics = prometheus_metrics.PrometheusMetrics('metrics_file')
        mock_load.assert_called_once_with('metrics_file')
        assert metrics.queries == 'queries'

    @mock.patch('hanadb_exporter.prometheus_metrics.Query.get_model')
    @mock.patch('json.load')
    @mock.patch('hanadb_exporter.prometheus_metrics.open')
    def test_load_metrics(self, mock_open, mock_json_load, mock_get_model):
        query1_data = mock.Mock()
        query2_data = mock.Mock()
        mock_json_load.return_value = {'query1': query1_data, 'query2': query2_data}

        mock_get_model.side_effect = ['data1', 'data2']

        queries = prometheus_metrics.PrometheusMetrics.load_metrics('metrics.json')
        mock_open.assert_called_once_with('metrics.json', 'r')

        mock_get_model.assert_has_calls([
            mock.call('query1', query1_data),
            mock.call('query2', query2_data)
        ], any_order=True)

        assert queries == ['data1', 'data2']

    @mock.patch('hanadb_exporter.prometheus_metrics.Query.get_model')
    @mock.patch('json.load')
    @mock.patch('hanadb_exporter.prometheus_metrics.open')
    @mock.patch('logging.Logger.error')
    def test_load_metrics_error(self, mock_logger, mock_open, mock_json_load, mock_get_model):
        query1_data = mock.Mock()
        query2_data = mock.Mock()
        mock_json_load.return_value = {'query1': query1_data, 'query2': query2_data}

        mock_get_model.side_effect = ['data1', TypeError('my-error')]

        with pytest.raises(TypeError) as err:
            prometheus_metrics.PrometheusMetrics.load_metrics('metrics.json')

        assert 'my-error' in str(err.value)
        mock_open.assert_called_once_with('metrics.json', 'r')

        mock_get_model.assert_has_calls([
            mock.call('query1', query1_data),
            mock.call('query2', query2_data)
        ], any_order=True)

        assert mock_logger.call_count == 2
