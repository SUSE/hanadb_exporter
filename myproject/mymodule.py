"""
:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2018-11-13
"""

import logging

class MyModule:
    """
    Example module to show have to create a new one
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._my_values = []

    def append_value(self, new_value):
        """
        Add a new value to `my_values` list

        Args:
            new_value (any): New value to append to the list
        """
        self._my_values.append(new_value)

    def clean(self):
        """
        Clean `my_values` list
        """
        self._my_values = []
        self._logger.info('The list now is clean!')

    def show(self):
        """
        Show values in `my_values` list
        """
        for i, value in enumerate(self._my_values):
            self._logger.info('%d: %s', i+1, value)

    def first_value(self):
        """
        Returns first value of my_values` list

        Returns:
            any: First value of my_values` list
        Raises:
            IndexError: my_values` list is empty
        """

        return self._my_values[0]
