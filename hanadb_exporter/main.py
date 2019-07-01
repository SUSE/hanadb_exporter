"""
SAP HANA database prometheus data exporter app

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

import sys
import traceback
import logging
from logging.config import fileConfig
import time
import json
import argparse

from shaptools import hdb_connector

from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server

from hanadb_exporter import exporter_factory


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
        "-m", "--metrics", help="Path to hanadb_exporter metrics file", required=True)
    parser.add_argument(
        "--verbosity",
        help="Python logging level. Options: DEBUG, INFO, WARN, ERROR (INFO by default)")
    args = parser.parse_args()
    return args


def setup_logging(config):
    """
    Setup logging system
    """
    hana_config = config.get('hana')
    sufix = 'hanadb_exporter_{}_{}'.format(hana_config.get('host'), hana_config.get('port', 30015))
    log_file = config.get('logging').get('log_file', '/var/log/{}'.format(sufix))

    fileConfig(config.get('logging').get('config_file'), defaults={'logfilename': log_file})

    # The next method is used to recatch and raise all
    # exceptions to redirect them to the logging system
    def handle_exception(*exc_info):
        """
        Catch exceptions to log them
        """
        text = ''.join(traceback.format_exception(*exc_info))
        logging.getLogger('hanadb_exporter').error(text)

    sys.excepthook = handle_exception


# Start up the server to expose the metrics.
def run():
    """
    Main execution
    """
    args = parse_arguments()
    config = parse_config(args.config)

    if config.get('logging', None):
        setup_logging(config)
    else:
        logging.basicConfig(level=args.verbosity or logging.INFO)

    metrics = args.metrics

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
        exporter_type='prometheus', metrics_file=metrics, hdb_connector=connector)
    REGISTRY.register(collector)
    start_http_server(config.get('exposition_port', 30015), '0.0.0.0')
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()
