"""
SAP HANA database prometheus data exporter

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import logging

from prometheus_client import core

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
                if column_name in metric.labels:
                    labels.append(column_value)
                if metric.value == '':
                    raise ValueError('No value specified in metrics.json for {}'.format(
                        metric.name))
                elif column_name == metric.value:
                    metric_value = column_value
            metric_obj.add_metric(labels, metric_value)
        self._logger.debug('%s \n', metric_obj.samples)
        return metric_obj

    def collect(self):
        """
        Collect data from database
        """

        for query in self._metrics_config.queries:
            #  execute each query once (only if enabled)
            if query.enabled and self._hana_version >= query.hana_version:
                # TODO: manage query error in an exception
                query_result = self._hdb_connector.query(query.query)
                formatted_query_result = utils.format_query_result(query_result)
                for metric in query.metrics:
                    if metric.type == "gauge":
                        metric_obj = self._manage_gauge(metric, formatted_query_result)
                        yield metric_obj
                    else:
                        raise NotImplementedError('{} type not implemented'.format(metric.type))
            else:
                self._logger.info(
                    'Query %s is disabled or only available in higher hana versions', query.query)
