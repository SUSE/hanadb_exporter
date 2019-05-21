"""
SAP HANA database prometheus data exporter

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import logging

# TODO: In order to avoid dependencies, import custom prometheus client
try:
    from prometheus_client import core
except ImportError:
    # Load custom prometheus client
    raise NotImplementedError('custom prometheus client not implemented')

from hanadb_exporter.exporters.prometheus_metrics import METRICS


class MalformedMetric(Exception):
    """
    Metric malformed method
    """


class SapHanaCollector(object):
    """
    SAP HANA database data exporter
    """

    def __init__(self, conector):
        super(SapHanaCollector, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._hdb_connector = conector

    def _execute(self, metric):
        """
        Create metric object

        Args:
            metric (dict): query, info, type structure dictionary
        """
        try:
            value = self._hdb_connector.query(metric['query'])

            if metric['type'] == core.GaugeMetricFamily:
                metric_obj = self._manage_gauge(metric, value)
            else:
                raise NotImplementedError('{} type not implemented'.format(metric['type']))

            return metric_obj
        except KeyError as err:
            raise MalformedMetric(err)

    def _manage_gauge(self, metric, value):
        """
        Manage Gauge type metric
        """
        # Label not set
        metric_obj = core.GaugeMetricFamily(*metric['info'])
        if not metric['info'][3]:
            metric_obj.add_metric([], str(value[0][-1]))
        else:
            for label_item in value:
                self._logger.info('%s: %s' % (label_item[0], label_item[1]))

        return metric_obj

    def collect(self):
        """
        Collect data from database
        """
        for metric in METRICS:
            metric_obj = self._execute(metric)
            yield metric_obj
