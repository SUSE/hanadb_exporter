"""
Unitary tests for your_module.py.

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2018-11-13
"""

# pylint:disable=C0103,C0111,W0212,W0611

import logging
import unittest

import mock

from .. import myproject

class TestYourClassName(unittest.TestCase):
    """
    Unitary tests for YourClassName.
    """

    @classmethod
    def setUpClass(cls):
        """
        Global setUp.
        """

        logging.basicConfig(level=logging.INFO)

    def setUp(self):
        """
        Test setUp.
        """

    def tearDown(self):
        """
        Test tearDown.
        """

    @classmethod
    def tearDownClass(cls):
        """
        Global tearDown.
        """
