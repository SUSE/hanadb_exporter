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

from hanadb_exporter import prometheus_exporter

RECONNECTION_INTERVAL = 15
LOGGER = logging.getLogger(__name__)


def parse_config(config_file):
    """
    Parse config file
    """
    with open(config_file, 'r') as f_ptr:
        json_data = json.load(f_ptr)
    return json_data


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Path to hanadb_exporter configuration file", required=True)
    parser.add_argument(
        "-m", "--metrics", help="Path to hanadb_exporter metrics file", required=True)
    parser.add_argument(
        "-v", "--verbosity",
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
    def handle_exception(*exc_info): # pragma: no cover
        """
        Catch exceptions to log them
        """
        text = ''.join(traceback.format_exception(*exc_info))
        logging.getLogger('hanadb_exporter').error(text)

    sys.excepthook = handle_exception


def connect(connector, config):
    """
    Connect to HANA. This operation is repeated until successfull connection. The exporter will
    start working after that
    """
    hana_config = config['hana']
    LOGGER.info(
        'connecting to the hana database (%s:%s)',
        hana_config['host'], hana_config.get('port', 30015))
    while True:
        try:
            connector.connect(
                hana_config['host'],
                hana_config.get('port', 30015),
                user=hana_config['user'],
                password=hana_config['password'],
                RECONNECT='FALSE'
            )
            break
        except hdb_connector.connectors.base_connector.ConnectionError as err:
            LOGGER.error(
                'the connection to the database failed. error message: %s', str(err))
            time.sleep(RECONNECTION_INTERVAL)


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
        connect(connector, config)
    except KeyError as err:
        raise KeyError('Configuration file {} is malformed: {} not found'.format(args.config, err))

    hana_version = prometheus_exporter.SapHanaCollector.get_hana_version(connector)
    LOGGER.info('SAP HANA database version: %s', hana_version)

    collector = prometheus_exporter.SapHanaCollector(
        connector=connector, metrics_file=metrics, hana_version=hana_version)

    REGISTRY.register(collector)
    LOGGER.info('exporter sucessfully registered')
    LOGGER.info('starting to serve metrics')
    start_http_server(config.get('exposition_port', 8001), '0.0.0.0')
    while True:
        time.sleep(1)

if __name__ == "__main__": # pragma: no cover
    run()
