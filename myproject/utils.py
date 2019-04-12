"""
:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2018-11-13
"""

import logging

def welcome(name):
    """
    Welcome newcomer with a message

    Args:
        name (str): Newcomer name
    """

    logging.getLogger(__name__).info('Hello %s!', name)

def farewell(name):
    """
    Farewell the newcomer

    Args:
        name (str): Newcomer name
    """

    logging.getLogger(__name__).info('Farewell %s!', name)
