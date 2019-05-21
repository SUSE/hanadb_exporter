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
    # Memory Metrics
    {
        'query': 'SELECT ROUND(SUM(total_memory_used_size/1024/1024),2) used_memory_mb FROM m_service_memory;',
        'info': ('hanadb_total_used_memory', 'Total used memory in MB', None, [], 'MB'),
        'type': core.GaugeMetricFamily
    },
    {
        'query': 'SELECT ROUND(SUM(memory_size_in_total)/1024/1024) column_tables_used_mb FROM m_cs_tables;',
        'info': ('hanadb_column_tables_used_memory', 'Column tables total memory used in MB', None, [], 'MB'),
        'type': core.GaugeMetricFamily
    },
    {
        'query': ' SELECT schema_name, ROUND(SUM(memory_size_in_total)/1024/1024) schema_memory_used_mb FROM m_cs_tables GROUP BY schema_name;',
        'info': ('hanadb_schema_used_memory', 'Total used memory by schema', None, ['schema', 'data'], 'MB'),
        'type': core.GaugeMetricFamily
    },
]
