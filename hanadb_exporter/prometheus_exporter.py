"""
SAP HANA database prometheus data exporter

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import logging

from prometheus_client import core
from shaptools import hdb_connector
from hanadb_exporter import prometheus_metrics
from hanadb_exporter import utils


class SapHanaCollector(object):
    """
    SAP HANA database data exporter
    """

    def __init__(self, connector, metrics_file, hana_version):
        self._logger = logging.getLogger(__name__)
        self._hdb_connector = connector
        # metrics_config contains the configuration api/json data
        self._metrics_config = prometheus_metrics.PrometheusMetrics(metrics_file)
        self._hana_version = hana_version

    @staticmethod
    def get_hana_version(connector):
        """
        Query the SAP HANA database version

        Args:
            connector: HANA database api connector
        """
        query = 'SELECT * FROM sys.m_database;'
        query_result = connector.query(query)
        return utils.format_query_result(query_result)[0]['VERSION']

    def _manage_gauge(self, metric, formatted_query_result):
        """
        Manage Gauge type metric:
        metric is the json.file object for example
        parse a SQL query and fullfill(formatted_query_result) the metric object from prometheus

        Args:
            metric (dict): a dictionary containing information about the metric
            formatted_query_result (nested list): query formated by _format_query_result method
        """
        metric_obj = core.GaugeMetricFamily(
            metric.name, metric.description, None, metric.labels, metric.unit)
        for row in formatted_query_result:
            labels = []
            metric_value = None
            for column_name, column_value in row.items():
                try:
                    labels.insert(metric.labels.index(column_name.lower()), column_value)
                except ValueError:  # Received data is not a label, check for the lowercased value
                    if column_name.lower() == metric.value.lower():
                        metric_value = column_value
            if metric_value is None:
                raise ValueError(
                    'Specified value in metrics.json for metric'
                    ' "{}": ({}) not found in the query result'.format(
                        metric.name, metric.value))
            elif len(labels) != len(metric.labels):
                # Log when a label(s) specified in metrics.json is not found in the query result
                raise ValueError(
                    'One or more label(s) specified in metrics.json'
                    ' for metric: "{}" is not found in the the query result'.format(
                        metric.name))
            else:
                metric_obj.add_metric(labels, metric_value)
        self._logger.debug('%s \n', metric_obj.samples)
        return metric_obj

    def collect(self):
        """
        execute db queries defined by metrics_config/api file, and store them in
        a prometheus metric_object, which will be served over http for scraping e.g gauge, etc.
        """
        # Try to reconnect if the connection is lost. It will raise an exception is case of error
        self._hdb_connector.reconnect()

        for query in self._metrics_config.queries:
            if not query.enabled:
                self._logger.info('Query %s is disabled', query.query)
            elif not utils.check_hana_range(self._hana_version, query.hana_version_range):
                self._logger.info('Query %s out of the provided hana version range: %s',
                                  query.query, query.hana_version_range)
            else:
                try:
                    query_result = self._hdb_connector.query(query.query)
                except hdb_connector.connectors.base_connector.QueryError as err:
                    self._logger.error('Failure in query: %s, skipping...', query.query)
                    self._logger.error(str(err))
                    continue  # Moving to the next iteration (query)
                formatted_query_result = utils.format_query_result(query_result)
                for metric in query.metrics:
                    if metric.type == "gauge":
                        try:
                            metric_obj = self._manage_gauge(metric, formatted_query_result)
                        except ValueError as err:
                            self._logger.error(str(err))
                            # If an a ValueError exception is caught, skip the metric and go on to
                            # complete the rest of the loop
                            continue
                    else:
                        raise NotImplementedError('{} type not implemented'.format(metric.type))
                    yield metric_obj
