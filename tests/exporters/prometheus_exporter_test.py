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

from hanadb_exporter.exporters.prometheus_exporter import SapHanaCollector, MalformedMetric

# class TestMyModule(unittest.TestCase):
#     """
#     Unitary tests for YourClassName.
#     """

#     @classmethod
#     def setUpClass(cls):
#         """
#         Global setUp.
#         """

#         logging.basicConfig(level=logging.INFO)

#     def setUp(self):
#         """
#         Test setUp.
#         """
#         self._test_module = mymodule.MyModule()

#     def tearDown(self):
#         """
#         Test tearDown.
#         """

#     @classmethod
#     def tearDownClass(cls):
#         """
#         Global tearDown.
#         """

#     def test_append_value(self):
#         self._test_module.append_value(5)
#         self.assertEqual(5, self._test_module._my_values[-1])

#         self._test_module.append_value('hello')
#         self.assertEqual('hello', self._test_module._my_values[-1])

#     def test_clean(self):
#         self._test_module._my_values.append(5)
#         self._test_module.clean()
#         self.assertEqual([], self._test_module._my_values)

#     @mock.patch('logging.Logger.info')
#     def test_show(self, logger):
#         self._test_module._my_values.append(5)
#         self._test_module._my_values.append(15)
#         self._test_module._my_values.append(25)

#         self._test_module.show()

#         logger.assert_has_calls([
#             mock.call('%d: %s', 1, 5),
#             mock.call('%d: %s', 2, 15),
#             mock.call('%d: %s', 3, 25)
#         ])

#     def test_first_value(self):
#         self._test_module._my_values.append(5)
#         value = self._test_module.first_value()
#         self.assertEqual(5, value)

#     def test_first_value_empty(self):
#         with self.assertRaises(IndexError):
#             self._test_module.first_value()

#     @mock.patch('logging.Logger.info')
#     def test_welcome(self, logger):
#         utils.welcome('xarbulu')
#         logger.assert_called_once_with("Hello %s!", 'xarbulu')

#     @mock.patch('logging.Logger.info')
#     def test_farewell(self, logger):
#         utils.farewell('xarbulu')
#         logger.assert_called_once_with("Farewell %s!", 'xarbulu')
