"""
SAP HANA database exporter factory

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-06-13
"""

import logging

from hanadb_exporter.exporters import prometheus_exporter
from hanadb_exporter import utils


class SapHanaExporter(object):
    """
    SAP HANA factory exporter

    Args:
        exporter_type (str): Exporter type. Options: prometheus
        metrics_file (str): Path to the metrics file
        hdb_connector (hdb_connector.HdbConnector): SAP HANA database connector
    """

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

    @classmethod
    def create(cls, exporter_type='prometheus', **kwargs):
        """
        Create SAP HANA exporter
        """
        cls._logger = logging.getLogger(__name__)
        connector = kwargs.get('hdb_connector')
        hana_version = cls.get_hana_version(connector)
        cls._logger.info('SAP HANA database version: %s', hana_version)
        if exporter_type == 'prometheus':
            cls._logger.info('prometheus exporter selected')
            collector = prometheus_exporter.SapHanaCollector(
                connector=connector,
                metrics_file=kwargs.get('metrics_file'),
                hana_version=hana_version
            )
            return collector
        else:
            raise NotImplementedError(
                '{} exporter not implemented'.format(exporter_type))
