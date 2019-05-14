"""
SAP HANA database prometheus data exporter app

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import logging
import time
import json

from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server

import hanadb_exporter
from shaptools import hdb_connector

CONFIG_FILE = './config.json'


def parse_config(config_file):
    """
    Parse config file
    """
    with open(config_file, 'r') as f_ptr:
        json_data = json.load(f_ptr)
    return json_data


# Start up the server to expose the metrics.
def main():
    logging.basicConfig(level=logging.INFO)
    config = parse_config(CONFIG_FILE)

    connector = hdb_connector.HdbConnector()
    try:
        hana_config = config.get('hana')
        connector.connect(
            hana_config.get('host'),
            hana_config.get('port', 30015),
            user=hana_config.get('user'),
            password=hana_config.get('password')
        )
    except KeyError as err:
        raise KeyError('Configuration file {} is malformed: {}'.format(CONFIG_FILE, err))
    collector = hanadb_exporter.SapHanaExporter.create(
        exporter_type='prometheus', hdb_connector=connector)
    REGISTRY.register(collector)
    start_http_server(config.get('exposition_port', 30015), '0.0.0.0')
    while True: time.sleep(1)

if __name__ == "__main__":
    main()
