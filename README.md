# SAP HANA Database exporter

[![Exporter CI](https://github.com/SUSE/hanadb_exporter/workflows/Exporter%20CI/badge.svg)](https://github.com/SUSE/hanadb_exporter/actions?query=workflow%3A%22Exporter+CI%22)
[![Dashboards CI](https://github.com/SUSE/hanadb_exporter/workflows/Dashboards%20CI/badge.svg)](https://github.com/SUSE/hanadb_exporter/actions?query=workflow%3A%22Dashboards+CI%22)

Prometheus exporter written in Python, to export SAP HANA database metrics. The
project is based in the official prometheus exporter: [prometheus_client](https://github.com/prometheus/client_python).

The exporter is able to export the metrics from more than 1 database/tenant if the `multi_tenant` option is enabled in the configuration file (enabled by default).

The labels `sid` (system identifier), `insnr` (instance number), `database_name` (database name) and `host` (machine hostname) will be exported for all the metrics.


## Prerequisites

1. A running and reachable SAP HANA database (single or multi container). Running the exporter in the
same machine where the HANA database is running is recommended. Ideally each database
should be monitored by one exporter.

2. A SAP HANA Connector, for that, you have two options:
  - [`dbapi` (SAP/official)](https://help.sap.com/viewer/1efad1691c1f496b8b580064a6536c2d/Cloud/en-US/39eca89d94ca464ca52385ad50fc7dea.html)
  - [`pyhdb` (unofficial/open source)](https://github.com/SAP/PyHDB)

The installation of the connector is covered in the [Installation](#installation) section.

3. Some metrics are collected on the HANA monitoring views by the [SAP Host agent](https://help.sap.com/saphelp_nwpi711/helpdata/en/21/98c443122744efae67c0352033691d/frameset.htm). Make sure to have it installed and running to have access to all the monitoring metrics.


## Metrics file

The exporter uses an additional file to know the metrics that are going to be exported. Here more information about the [metrics file](./docs/METRICS.md).

## Installation

The project can be installed in many ways, including but not limited to:

1. [RPM](#rpm)
2. [Manual clone](#manual-clone)

### RPM

On openSUSE or SUSE Linux Enterprise use `zypper` package manager:
```shell
zypper install prometheus-hanadb_exporter
```

Find the latest development repositories at [SUSE's Open Build Service](https://build.opensuse.org/package/show/network:ha-clustering:sap-deployments:devel/prometheus-hanadb_exporter).

### Manual clone

> The exporter is developed to be used with Python3.\
> The usage of a virtual environment is recommended.

```
git clone https://github.com/SUSE/hanadb_exporter
cd hanadb_exporter # project root folder
virtualenv virt
source virt/bin/activate
# uncomment one of the next two options (to use hdbcli, you will need to have the HANA client folder where this python package is available)
# pip install pyhdb
# pip install path-to-hdbcli-N.N.N.tar.gaz
pip install .
# pip install -e . # To install in development mode
# deactivate # to exit from the virtualenv
```

If you prefer, you can install the PyHDB SAP HANA connector as a RPM package doing (example for Tumbleweed, but available for other versions):

```
# All the commands must be executed as root user
zypper addrepo https://download.opensuse.org/repositories/network:/ha-clustering:/sap-deployments:/devel/openSUSE_Tumbleweed/network:ha-clustering:sap-deployments:devel.repo
zypper ref
zypper in python3-PyHDB
```

## Configuring the exporter

Create the `config.json` configuration file.
An example of `config.json` available in [config.json.example](config.json.example). Here the most
important items in the configuration file:
  - `listen_address`: Address where the prometheus exporter will be exposed (0.0.0.0 by default).
  - `exposition_port`: Port where the prometheus exporter will be exposed (9968 by default).
  - `multi_tenant`: Export the metrics from other tenants. To use this the connection must be done with the System Database (port 30013).
  - `timeout`: Timeout to connect to the database. After this time the app will fail (even in daemon mode).
  - `hana.host`: Address of the SAP HANA database.
  - `hana.port`: Port where the SAP HANA database is exposed.
  - `hana.userkey`: Stored user key. This is the secure option if you don't want to have the password in the configuration file. The `userkey` and `user/password` are self exclusive being the first the default if both options are set.
  - `hana.user`: An existing user with access right to the SAP HANA database.
  - `hana.password`: Password of an existing user.
  - `hana.ssl`: Enable SSL connection (False by default). Only available for `dbapi` connector
  - `hana.ssl_validate_cert`: Enable SSL certification validation. This field is required by HANA cloud. Only available for `dbapi` connector
  - `hana.aws_secret_name`: The secret name containing the username and password. This is a secure option to use AWS secrets manager if SAP HANA database is stored on AWS. `aws_secret_name` and `user/password` are self exclusive, `aws_secret_name` is the default if both options are set.
  - `logging.config_file`: Python logging system configuration file (by default WARN and ERROR level messages will be sent to the syslog)
  - `logging.log_file`: Logging file (/var/log/hanadb_exporter.log by default)

The logging configuration file follows the python standard logging system style: [Python logging](https://docs.python.org/3/library/logging.config.html).

Using the default [configuration file](./logging_config.ini), it will redirect the logs to the file assigned in the [json configuration file](./config.json.example) and to the syslog (only logging level up to WARNING).

### Using the stored user key

This is the recommended option if we want to keep the database secure (for development environments the `user/password` with `SYSTEM` user can be used as it's faster to setup).
To use the `userkey` option the `dbapi` must be installed (usually stored in `/hana/shared/PRD/hdbclient/hdbcli-N.N.N.tar.gz` and installable with pip3).
It cannot be used from other different client (the key is stored in the client itself). This will raise the `hdbcli.dbapi.Error: (-10104, 'Invalid value for KEY')` error.
For that a new stored user key must be created with the user that is running python. For that (please, notice that the `hdbclient` is the same as the `dbapi` python package):
```
/hana/shared/PRD/hdbclient/hdbuserstore set yourkey host:30013@SYSTEMDB hanadb_exporter pass
```

### Using AWS Secrets Manager

If SAP HANA database is stored on AWS EC2 instance, this is a secure option to store the `user/password` without having them in the configuration file. 
To use this option:
- Create a [secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/manage_create-basic-secret.html) in key/value pairs format, specify Key `username` and then for Value enter the database user. Add a second Key `password` and then for Value enter the password.
For the secret name, enter a name for your secret, and pass that name in the configuration file as a value for `aws_secret_name` item. Secret json example:

```
{
  "username": "database_user",
  "password": "database_password"
}
```
- Allow read-only access from EC2 IAM role to the secret by attaching a [resource-based policy](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_resource-based-policies.html) to the secret. Policy Example:
```
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:role/EC2RoleToAccessSecrets"},
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*",
    }
  ]
}
```



Some tips:
- Set `SYSTEMDB` as default database, this way the exporter will know where to get the tenants data.
- Don't use the stored user key created for the backup as this is created using the sidadm user.
- The usage of a user with access only to the monitoring tables is recommended instead of using SYSTEM user.
- If a user with monitoring role is used the user must exist in all the databases (SYSTEMDB+tenants).

### Create a new user with monitoring role
Run the next commands to create a user with moniroting roles (**the commands must be executed in all the databases**):
```
su - prdadm
hdbsql -u SYSTEM -p pass -d SYSTEMDB #(PRD for the tenant in this example)
CREATE USER HANADB_EXPORTER_USER PASSWORD MyExporterPassword NO FORCE_FIRST_PASSWORD_CHANGE;
CREATE ROLE HANADB_EXPORTER_ROLE;
GRANT MONITORING TO HANADB_EXPORTER_ROLE;
GRANT HANADB_EXPORTER_ROLE TO HANADB_EXPORTER_USER;
```

## Running the exporter

Start the exporter by running the following command:
```
hanadb_exporter -c config.json -m metrics.json
# Or
python3 hanadb_exporter/main.py -c config.json -m metrics.json
```

If a `config.json` configuration file is stored in `/etc/hanadb_exporter` the exporter can be started with the next command too:
```
hanadb_exporter --identifier config # Notice that the identifier matches with the config file without extension
```

### Running as a daemon

The hanadb_exporter can be executed using `systemd`. For that, the best option is to install the project using the rpm package as described in [Installation](#installation).

After that we need to create the configuration file as `/etc/hanadb_exporter/my-exporter.json` (the name of the file is relevant as we will use it to start the daemon).
The [config.json.example](./config.json.example) can be used as example (the example file is stored in `/usr/etc/hanadb_exporter` folder too).

The default [metrics file](./metrics.json) is stored in `/usr/etc/hanadb_exporter/metrics.json`. If a new `metrics.json` is stored in `/etc/hanadb_exporter` this will be used.

The logging configuration file can be updated as well to customize changing the new configuration file `logging.config_file` entry (default one available in `/usr/etc/hanadb_exporter/logging_config.ini`).

Now, the exporter can be started as a daemon. As we can have multiple `hanadb_exporter` instances running in one machine, the service is created using a template file, so an extra information must be given to `systemd` (this is done adding the `@` keyword after the service name together with the name of the configuration file created previously in `/etc/hanadb_exporter/{name}.json`):
```
# All the command must be executed as root user
systemctl start prometheus-hanadb_exporter@my-exporter
# Check the status with
systemctl status prometheus-hanadb_exporter@my-exporter
# Enable the exporter to be started at boot time
systemctl enable prometheus-hanadb_exporter@my-exporter
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
