"""
Unitary tests for exporters/prometheus_exporter.py.

:author: abelarbi
:organization: SUSE Linux GmbH
:contact: abelarbi@suse.de

:since: 2019-06-11
"""

# pylint:disable=C0103,C0111,W0212,W0611

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import unittest

import mock

from hanadb_exporter.exporters.prometheus_exporter import SapHanaCollector, SapHanaCollector
class SapHanaCollector(unittest.TestCase):
    """
    Unitary tests for SapHanaCollector.
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
        self.SapHanaCollector = SapHanaCollector(kwargs.get('hdb_connector'))

    def tearDown(self):
        """
        Test tearDown.
        """

    @classmethod
    def tearDownClass(cls):
        """
        Global tearDown.
        """

    # def test_collect(self):


class SapHanaCollector(unittest.TestCase):
    """
    Unitary tests for SapHanaCollector.
    """

    @classmethod
    def setUpClass(cls):
        """
        Global setUp.
        """

        logging.basicConfig(level=logging.INFO)

    def tearDown(self):
        """
        Test tearDown.
        """

    @classmethod
    def tearDownClass(cls):
        """
        Global tearDown.
        """