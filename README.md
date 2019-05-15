# SAP HANA Database exporter

Prometheus exporter written in Python, to export SAP HANA database metrics. The
project is based in the official prometheus exporter: [prometheus_client](https://github.com/prometheus/client_python).


## Getting started
In order to start the prometheus exporter follow the next steps:

1. A SAP HANA database must be running an available. Running the exporter in the
same machine where the HANA database running is recommended. Ideally each database
should be monitored by one exporter.

2. `dbapi` or `pyhdb`, one of them, must be installed. The first one is the official
api provided by SAP. The second is an open source option. Here some links for that:
  - `dbapi`: https://help.sap.com/viewer/1efad1691c1f496b8b580064a6536c2d/Cloud/en-US/39eca89d94ca464ca52385ad50fc7dea.html
  - `pyhdb`: https://github.com/SAP/PyHDB

  How to install them expalined in the next step.

3. Install the project dependencies (the usage of a virtual environment is recommended).

  ```
  cd hanadb_exporter # project root folder
  virtualenv virt
  source virt/bin/activate
  pip install -r requirements.txt
  #uncomment one of the next two options
  #pip install pyhdb
  #pip install path-to-hdbcli-N.N.N.tar.gaz
  #deactivate # to exit from the virtualenv
  ```

4. Create the `config.json` configuration file and place it in the project root folder.
An example is available in [config.json.example](config.json.example). Here the most
important items in the configuration file:
  - `exposition_port`: Port where the prometheus exporter will be exposed.
  - `hana.host`: Address of the SAP HANA database.
  - `hana.port`: Port where the SAP HANA database is exposed.
  - `hana.user`: An existing user with access right to the SAP HANA database.
  - `hana.password`: Password of an existing user.


5. Start the exporter running the next command:
```
python app.py
```

## Dependencies

List of dependencies are specified in the ["Requirements file"](requirements.txt). Items can be installed using pip:

    pip install -r requirements.txt

## License

See the [LICENSE](LICENSE) file for license rights and limitations.

## Author

Xabier Arbulu Insausti (xarbulu@suse.com)

## Reviewers

*Pull request* preferred reviewers for this project:
- Xabier Arbulu Insausti (xarbulu@suse.com)

## References

https://prometheus.io/docs/instrumenting/writing_exporters/

https://prometheus.io/docs/practices/naming/

http://sap.optimieren.de/hana/hana/html/sys_statistics_views.html

https://help.sap.com/viewer/1efad1691c1f496b8b580064a6536c2d/Cloud/en-US/39eca89d94ca464ca52385ad50fc7dea.html
