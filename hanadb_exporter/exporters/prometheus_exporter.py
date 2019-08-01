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
from hanadb_exporter.exporters import prometheus_metrics
from hanadb_exporter import utils



class SapHanaCollector(object):
    """
    SAP HANA database data exporter
    """

    def __init__(self, connector, metrics_file, hana_version):
        self._logger = logging.getLogger(__name__)
        self._hdb_connector = connector
        # load metric configuration
        self._metrics_config = prometheus_metrics.PrometheusMetrics(metrics_file)
        self._hana_version = hana_version

    def _manage_gauge(self, metric, formatted_query_result):
        """
        Manage Gauge type metric

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
                # TODO: exception labels not found
                # TODO: exception value not found
                try:
                    labels.insert(metric.labels.index(column_name), column_value)
                except ValueError: # Received data is not a label, check for the value
                    if column_name == metric.value:
                        metric_value = column_value
            if metric_value != None:
                metric_obj.add_metric(labels, metric_value)
            else:
                self._logger.error('Specified value in metrics.json for metric'
                ' "%s": (%s) not found in the query result', metric.name, metric.value)

        self._logger.debug('%s \n', metric_obj.samples)
        return metric_obj

    def collect(self):
        """
        Collect data from database
        """
        for query in self._metrics_config.queries:
            if not query.enabled:
                self._logger.info('Query %s is disabled', query.query)
            elif not utils.check_hana_range(self._hana_version, query.hana_version_range):
                self._logger.info('Query %s out of the provided hana version range: %s',
                                  query.query, query.hana_version_range)
            else:
                try:
                    query_result = self._hdb_connector.query(query.query)
                    formatted_query_result = utils.format_query_result(query_result)
                    for metric in query.metrics:
                        if metric.type == "gauge":
                            metric_obj = self._manage_gauge(metric, formatted_query_result)
                            yield metric_obj
                        else:
                            raise NotImplementedError('{} type not implemented'.format(metric.type))
                except hdb_connector.connectors.base_connector.QueryError as err:
                    self._logger.logger.error('Failure in query: %s, skipping...', query.query)
                    self._logger.logger.error(err)
