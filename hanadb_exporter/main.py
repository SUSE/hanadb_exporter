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
import argparse

from shaptools import hdb_connector

from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server

import exporter_factory


def parse_config(config_file):
    """
    Parse config file
    """
    with open(config_file, 'r') as f_ptr:
        json_data = json.load(f_ptr)
    return json_data


def parse_arguments():
    """
    Parase command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Path to hanadb_exporter configuration file", required=True)
    parser.add_argument(
        "--verbosity",
        help="Python logging level. Options: DEBUG, INFO, WARN, ERROR (INFO by default)")
    args = parser.parse_args()
    return args


# Start up the server to expose the metrics.
def run():
    """
    Main execution
    """
    args = parse_arguments()
    logging.basicConfig(level=args.verbosity or logging.INFO)
    config = parse_config(args.config)

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
        raise KeyError('Configuration file {} is malformed: {}'.format(args.config, err))
    collector = exporter_factory.SapHanaExporter.create(
        exporter_type='prometheus', hdb_connector=connector)
    REGISTRY.register(collector)
    start_http_server(config.get('exposition_port', 30015), '0.0.0.0')
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()
