"""
SAP HANA database data exporter

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

__version__ = "0.1.0"

import logging

from hanadb_exporter.exporters import prometheus_exporter


class SapHanaExporter(object):
    """
    SAP HANA factory exporter

    Args:
        exporter_type (str): Exporter type. Options: prometheus
    """

    @classmethod
    def create(cls, exporter_type='prometheus', **kwargs):
        """
        Create SAP HANA exporter
        """
        cls._logger = logging.getLogger(__name__)
        if exporter_type == 'prometheus':
            cls._logger.info('prometheus exporter selected')
            collector = prometheus_exporter.SapHanaCollector(kwargs.get('hdb_connector'))
            return collector
        else:
            raise NotImplementedError(
                '{} exporter not implemented'.format(exporter_type))
