"""
SAP HANA database prometheus data exporter metrics

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-05-09
"""

# TODO: In order to avoid dependencies, import custom prometheus client
try:
    from prometheus_client import core
except ImportError:
    # Load custom prometheus client
    raise NotImplementedError('custom prometheus client not implemented')


METRICS = [
    {
        'query': 'SELECT ROUND(SUM(TOTAL_MEMORY_USED_SIZE/1024/1024), 2) AS "Used Memory MB" FROM M_SERVICE_MEMORY;',
        'info': ('hanadb_total_used_memory', 'Total used memory in MB', None, [], 'MB'),
        'type': core.GaugeMetricFamily
    },
    {
        'query': 'SELECT ROUND(SUM(MEMORY_SIZE_IN_TOTAL)/1024/1024) AS "Column Tables MB Used" FROM M_CS_TABLES;',
        'info': ('hanadb_column_tables_used_memory', 'Column tables total memory used in MB', None, [], 'MB'),
        'type': core.GaugeMetricFamily
    },
    {
        'query': 'SELECT SCHEMA_NAME AS "Schema", ROUND(SUM(MEMORY_SIZE_IN_TOTAL)/1024/1024) AS "MB Used" FROM M_CS_TABLES GROUP BY SCHEMA_NAME ORDER BY "MB Used" DESC;',
        'info': ('hanadb_schema_used_memory', 'Total used memory by schema', None, ['schema', 'data'], 'MB'),
        'type': core.GaugeMetricFamily
    },
]
