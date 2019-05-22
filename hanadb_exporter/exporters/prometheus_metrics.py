"""
SAP HANA database prometheus data exporter metrics

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import json

# TODO: In order to avoid dependencies, import custom prometheus client
try:
    from prometheus_client import core
except ImportError:
    # Load custom prometheus client
    raise NotImplementedError('custom prometheus client not implemented')

class PrometheusMetrics:
    def __init__(self):
        self.metrics = self.load_metrics()

    def load_metrics(self):
        with open('metrics.json') as metrics_file:
            data = json.load(metrics_file)
            return data
