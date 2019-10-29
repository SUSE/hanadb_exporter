"""
SAP HANA database manager

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-10-24
"""

import logging
import time

from shaptools import hdb_connector
from hanadb_exporter import utils

RECONNECTION_INTERVAL = 15


class DatabaseManager(object):
    """
    Manage the connection to a multi container HANA system
    """

    TENANT_DATA_QUERY =\
"""SELECT SQL_PORT FROM SYS_DATABASES.M_SERVICES
WHERE (SERVICE_NAME='indexserver' and COORDINATOR_TYPE= 'MASTER')"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._system_db_connector = hdb_connector.HdbConnector()
        self._db_connectors = []

    def _get_tenants_port(self):
        """
        Get tenants port
        """
        data = self._system_db_connector.query(self.TENANT_DATA_QUERY)
        formatted_data = utils.format_query_result(data)
        for tenant_data in formatted_data:
            yield int(tenant_data['SQL_PORT'])

    def _connect_tenants(self, host, user, password):
        """
        Connect to the tenants

        Args:
            host (str): Host of the HANA database
            user (str): System database user name (SYSTEM usually)
            password (str): System database user password
        """
        for tenant_port in self._get_tenants_port():
            conn = hdb_connector.HdbConnector()
            conn.connect(
                host, tenant_port, user=user, password=password, RECONNECT='FALSE')
            self._db_connectors.append(conn)

    def start(self, host, port, user, password, multi_tenant=True, timeout=600):
        """
        Start de database manager. This will open a connection with the System database and
        retrieve the current environemtn tenant databases data

        Args:
            host (str): Host of the HANA database
            port (int): Port of the System database (3XX13 when XX is the instance number)
            user (str): System database user name (SYSTEM usually)
            password (str): System database user password
            multi_tenant (bool): Connect to all tenants checking the data in the System database
            timeout (int, opt): Timeout in seconds to connect to the System database
        """
        current_time = time.time()
        timeout = current_time + timeout
        while current_time <= timeout:
            try:
                self._system_db_connector.connect(
                    host, port, user=user, password=password, RECONNECT='FALSE')
                self._db_connectors.append(self._system_db_connector)
                break
            except hdb_connector.connectors.base_connector.ConnectionError as err:
                self._logger.error(
                    'the connection to the system database failed. error message: %s', str(err))
                time.sleep(RECONNECTION_INTERVAL)
                current_time = time.time()
        else:
            raise hdb_connector.connectors.base_connector.ConnectionError(
                'timeout reached connecting the System database')

        if multi_tenant:
            self._connect_tenants(host, user, password)

    def get_connectors(self):
        """
        Get the connectors
        """
        return self._db_connectors
