[![Build Status](https://travis-ci.org/SUSE/hanadb_exporter.svg?branch=master)](https://travis-ci.org/SUSE/hanadb_exporter)
[![Maintainability](https://api.codeclimate.com/v1/badges/1fc3a80d4e8342fa6f0d/maintainability)](https://codeclimate.com/github/SUSE/hanadb_exporter/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/1fc3a80d4e8342fa6f0d/test_coverage)](https://codeclimate.com/github/SUSE/hanadb_exporter/test_coverage)

# SAP HANA Database exporter

Prometheus exporter written in Python, to export SAP HANA database metrics. The
project is based in the official prometheus exporter: [prometheus_client](https://github.com/prometheus/client_python).


## Prerequisites

1. A running and reachable SAP HANA database. Running the exporter in the
same machine where the HANA database is running is recommended. Ideally each database
should be monitored by one exporter.

2. A SAP HANA Connector, for that, you have two options:
  - [`dbapi` (SAP/official)](https://help.sap.com/viewer/1efad1691c1f496b8b580064a6536c2d/Cloud/en-US/39eca89d94ca464ca52385ad50fc7dea.html)
  - [`pyhdb` (unofficial/open source)](https://github.com/SAP/PyHDB)

The installation of the connector is covered in the `Installation` section.

## Installation
Note: The usage of a virtual environment is recommended.

```
cd hanadb_exporter # project root folder
virtualenv virt
source virt/bin/activate
# uncomment one of the next two options
# pip install pyhdb
# pip install path-to-hdbcli-N.N.N.tar.gaz
pip install .
# pip install -e . # To install in development mode
# deactivate # to exit from the virtualenv
```

## Configuring and running the exporter

1. Create the `config.json` configuration file.
An example of `config.json` available in [config.json.example](config.json.example). Here the most
important items in the configuration file:
  - `exposition_port`: Port where the prometheus exporter will be exposed.
  - `hana.host`: Address of the SAP HANA database.
  - `hana.port`: Port where the SAP HANA database is exposed.
  - `hana.user`: An existing user with access right to the SAP HANA database.
  - `hana.password`: Password of an existing user.
  - `logging.config_file`: Python logging system configuration file (by default WARN and ERROR level messages will be sent to the syslog)
  - `logging.log_file`: Logging file (/var/log/hanadb_exporter.log by default)

The logging configuration file follows the python standard logging system style: [Python logging](https://docs.python.org/3/library/logging.config.html).

Using the default [configuration file](./logging_config.ini), it will redirect the logs to the file assigned in the [json configuration file](./config.json.example) and to the syslog (only logging level up to WARNING).

2. Start the exporter by running the following command:
```
hanadb_exporter -c config.json -m metrics.json
# Or
python3 hanadb_exporter/main.py -c config.json -m metrics.json
```

## Running as a daemon
The hanadb_exporter can be executed using `systemd`. For that, the best option is to install the
project using a rpm package. This can be done following the next steps (this example is for tumbleweed):

```
# All the command must be executed as root user
zypper addrepo https://download.opensuse.org/repositories/network:/ha-clustering:/Factory/openSUSE_Tumbleweed/network:ha-clustering:Factory.repo
zypper ref
zypper in hanadb_exporter
```

Even using this way, the SAP HANA database connector package must be installed independently (see [Installation](#installation)).
After that we need to create the configuration file as `/etc/hanadb_exporter/config.json`.
The [config.json.example](./config.json.example) can be used as example (the example file is
stored in `/etc/hanadb_exporter` folder too).

The logging configuration file can be updated as well to customize it (stored in `/etc/hanadb_exporter/logging_config.ini`)

Now, the exporter can be started as a daemon:
```
# All the command must be executed as root user
systemctl start hanadb_exporter
# Check the status with
systemctl status hanadb_exporter
```

## License

See the [LICENSE](LICENSE) file for license rights and limitations.

## Authors

- Kristoffer Gronlund (kgronlund@suse.com)
- Xabier Arbulu Insausti (xarbulu@suse.com)
- Ayoub Belarbi (abelarbi@suse.com)
- Diego Akechi (dakechi@suse.com)

## Reviewers

*Pull request* preferred reviewers for this project:
- Kristoffer Gronlund (kgronlund@suse.com)
- Xabier Arbulu Insausti (xarbulu@suse.com)
- Ayoub Belarbi (abelarbi@suse.com)

## References

https://prometheus.io/docs/instrumenting/writing_exporters/

https://prometheus.io/docs/practices/naming/

http://sap.optimieren.de/hana/hana/html/sys_statistics_views.html

https://help.sap.com/viewer/1efad1691c1f496b8b580064a6536c2d/Cloud/en-US/39eca89d94ca464ca52385ad50fc7dea.html
