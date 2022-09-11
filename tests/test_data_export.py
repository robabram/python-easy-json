#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json

from tests.base_test import BaseTestCase
from python_easy_json import JSONObject


class TestDataExport(BaseTestCase):
    """ Test loading data into a JSONObject and exporting back out """

    def test_simple_json_text_export(self):
        """ Test converting a simple JSON string to a JSONObject"""
        data = """{"key_2": 123, "key_1": "value_1"}"""
        obj = JSONObject(data, ordered=True)
        export = obj.to_json()

        self.assertIsInstance(obj, JSONObject)
        self.assertEqual(data, export)

    def test_simple_dict_export(self):
        """ Test converting a simple JSON string to a JSONObject"""
        data = {"key_1": "value_1", "key_2": 123}
        obj = JSONObject(data)
        export = obj.to_dict()

        self.assertIsInstance(obj, JSONObject)
        self.assertEqual(data, export)

    def test_nested_1_text_export(self):
        """ Test nested as a JSON export"""
        data = json.loads(self.json_data.nested_data_1)
        obj = JSONObject(data, ordered=True)

        export = obj.to_json(indent=2)
        self.assertIsInstance(export, str)

    def test_nested_1_dict_export(self):
        """ Test nested """
        data = json.loads(self.json_data.nested_data_1)
        obj = JSONObject(data)

        export = obj.to_dict()
        self.assertEqual(data, export)
