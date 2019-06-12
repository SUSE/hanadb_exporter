"""
Unitary tests for hanadb_exporter/__init__.py.

:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2019-06-12
"""

# pylint:disable=C0103,C0111,W0212,W0611

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import hanadb_exporter

class TestHanaDBExporter(unittest.TestCase):
    """
    Unitary tests for hanadb_exporter/__init__.py.
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

    def test_dummy(self):
        """
        Test created to just enable the CI in travis
        """
        pass
