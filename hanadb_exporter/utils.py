"""
Generic methods

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2019-07-04
"""

# TODO: this method could go in shaptools itself, providng the query return formatted if
# it is requested (returning a list of dictionaries like this method)
def format_query_result(query_result):
    """
    Format query results to match column names with their values for each row
    Returns: list containing a dictionaries (column_name, value)

    Args:
        query_result (obj): QueryResult object
    """
    formatted_query_result = []
    query_columns = [meta[0] for meta in query_result.metadata]
    for record in query_result.records:
        record_data = {}
        for index, record_item in enumerate(record):
            record_data[query_columns[index]] = record_item

        formatted_query_result.append(record_data)
    return formatted_query_result
