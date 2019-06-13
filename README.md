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
An example is available in [config.json.example](config.json.example). Here the most
important items in the configuration file:
  - `exposition_port`: Port where the prometheus exporter will be exposed.
  - `hana.host`: Address of the SAP HANA database.
  - `hana.port`: Port where the SAP HANA database is exposed.
  - `hana.user`: An existing user with access right to the SAP HANA database.
  - `hana.password`: Password of an existing user.

2. Start the exporter by running the following command:
```
hanadb_exporter -c config.json
# Or
python hanadb_exporter/main.py -c config.json
```

## License

See the [LICENSE](LICENSE) file for license rights and limitations.

## Authors

- Kristoffer Grönlund (kgronlund@suse.com)
- Xabier Arbulu Insausti (xarbulu@suse.com)
- Ayoub Belarbi (abelarbi@suse.com)

## Reviewers

*Pull request* preferred reviewers for this project:
- Kristoffer Grönlund (kgronlund@suse.com)
- Xabier Arbulu Insausti (xarbulu@suse.com)
- Ayoub Belarbi (abelarbi@suse.com)

## References

https://prometheus.io/docs/instrumenting/writing_exporters/

https://prometheus.io/docs/practices/naming/

http://sap.optimieren.de/hana/hana/html/sys_statistics_views.html

https://help.sap.com/viewer/1efad1691c1f496b8b580064a6536c2d/Cloud/en-US/39eca89d94ca464ca52385ad50fc7dea.html
