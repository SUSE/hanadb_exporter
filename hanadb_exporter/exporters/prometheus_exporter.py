"""
SAP HANA database prometheus data exporter

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import logging
import itertools

# TODO: In order to avoid dependencies, import custom prometheus client
try:
    from prometheus_client import core
except ImportError:
    # Load custom prometheus client
    raise NotImplementedError('custom prometheus client not implemented')

from hanadb_exporter.exporters.prometheus_metrics import PrometheusMetrics


class MalformedMetric(Exception):
    """
    Metric malformed method
    """


class SapHanaCollector(object):
    """
    SAP HANA database data exporter
    """

    def __init__(self, connector):
        super(SapHanaCollector, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._hdb_connector = connector

    def _execute(self, query):
        """
        Execute query and return a QueryResult object

        Args:
            query (string): SQL query
        """
        try:
            query_result = self._hdb_connector.query(query)
            return query_result
        except KeyError as err:
            raise MalformedMetric(err)

    def _format_query_result(self, query_result):
        """
        Format query results to match column names with their values for each row
        Returns nested list, containing tuples (column_name, value)

        Args:
            query_result (obj): QueryResult object
        """
        query_columns = []
        formatted_query_result = []
        for meta in query_result.metadata:
            query_columns.append(meta[0])
        for record in query_result.records:
            formatted_query_result.append(list(itertools.izip(query_columns, record)))
        return formatted_query_result

    def _manage_gauge(self, metric, formatted_query_result):
        """
        Manage Gauge type metric

        Args:
            metric (dict): a dictionary containing information about the metric
            formatted_query_result (nested list): query formated by _format_query_result method
        """
        metric_obj = core.GaugeMetricFamily(metric['name'], metric['description'], None, metric['labels'], metric['unit'])
        for row in formatted_query_result:
            labels = []
            value = 0
            for cell in row:
                # each cell is a tuple (column_name, value)
                if cell[0] in metric['labels']:
                    labels.append(cell[1])
                if cell[0] == metric['value']:
                    value = cell[1]
            metric_obj.add_metric(labels, value)
        self._logger.info('%s \n', metric_obj.samples)
        return metric_obj

    def collect(self):
        """
        Collect data from database
        """
        # load metric configuration
        metrics_config = PrometheusMetrics()
        for query, metrics in metrics_config.data.items():
            #  execute each query once
            query_result = self._execute(query)
            print('this is the query result \n')
            print(type(query_result))
            formatted_query_result = self._format_query_result(query_result)
            for metric in metrics:
                if metric['type'] == "gauge":
                    metric_obj = self._manage_gauge(metric, formatted_query_result)
                    yield metric_obj
                else:
                    raise NotImplementedError('{} type not implemented'.format(metric['type']))