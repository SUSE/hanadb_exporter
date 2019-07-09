# Metrics file

This document explains how to create/update the used metrics file in order to provide to the hanadb_exporter the required information to run the queries and export the data.

# JSON format

If the metrics file uses JSON format ([metrics.json](../metrics.json)) these are the available options
to create the correct structure:

Each entry in the JSON file is formed by a SAP HANA SQL query (key) and the metrics/additional information (value). The additional information is composed by:

* `enabled (boolean, optional)`: If the query is executed or not (`true` by default is the `enabled` entry is not set). If set to `false` the metrics for this query won't be executed.
* `hana_version_range (list, optional)`: The SAP HANA database versions range where the query is available (`[1.0.0]` by default). If the current database version is not inside the provided range, the query won't be executed. If the list has only one element, all versions beyond this value (this included) will be queried.
* `metrics (list)`: A list of metrics for this query. Each metric will need the next information;
* `name (str):`: The name used to export the metric.
* `description (str)`: The description of the metric (available as `# HELP`).
* `labels (list)`: List of labels used to split the records.
* `value (str)`: The name of the column used to gather the exported value (must match with one of the columns of the query).
* `unit (str):`: Used unit for the exported value (`mb` for example).
* `type (enum{gauge})`: Type of the exported metric (available options: `gauge`).

Here an example of a query and some metrics:

```
{
  "SELECT TOP 10 host, LPAD(port, 5) port, SUBSTRING(REPLACE_REGEXPR('\n' IN statement_string WITH ' ' OCCURRENCE ALL), 1,30) sql_string, statement_hash sql_hash, execution_count, total_execution_time + total_preparation_time total_elapsed_time FROM sys.m_sql_plan_cache ORDER BY total_elapsed_time, execution_count DESC;":
  {
    "enabled": true,
    "hana_version_range": ["1.0"]
    "metrics": [
      {
        "name": "hanadb_sql_top_time_consumers",
        "description": "Top statements time consumers. Sum of the time consumed in all executions in Microseconds",
        "labels": ["HOST", "PORT", "SQL_STRING", "SQL_HASH"],
        "value": "TOTAL_ELAPSED_TIME",
        "unit": "mu",
        "type": "gauge"
      },
      {
        "name": "hanadb_sql_top_time_consumers",
        "description": "Top statements time consumers. Number of total executions of the SQL Statement",
        "labels": ["HOST", "PORT", "SQL_STRING", "SQL_HASH"],
        "value": "EXECUTION_COUNT",
        "unit": "count",
        "type": "gauge"
      }
    ]
  }
}
```
