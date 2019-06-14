"""
SAP HANA database prometheus data exporter metrics

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import json


class PrometheusMetrics(object):
    """
    Class to store the metrics data
    """

    def __init__(self, metrics_file):
        self.data = self.load_metrics(metrics_file)

    @classmethod
    def load_metrics(cls, metrics_file):
        """
        Load metrics file as json
        """
        with open(metrics_file, 'r') as file_ptr:
            data = json.load(file_ptr)
        return data
