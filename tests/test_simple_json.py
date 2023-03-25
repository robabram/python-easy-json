#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json

from tests.base_test import BaseTestCase
from python_easy_json import JSONObject


class TestSimpleDict(BaseTestCase):

    def test_simple_ordered_data(self):
        """ Test simple JSON, no type casting. """
        obj = JSONObject(self.json_data.simple)

        self.assertIsInstance(obj, JSONObject)

        self.assertEqual(obj.field_bool, "true")
        self.assertEqual(obj.field_int, 123)
        self.assertEqual(obj.field_float, 456.789)
        self.assertEqual(obj.field_date, '2022-09-09')
        self.assertEqual(obj.field_datetime, '2022-09-19 10:11:01.123456')

    def test_dictionary_string_value(self):
        """ Test case where value for key is a JSON string """
        data = json.loads(self.json_data.simple)
        data['field_embedded'] = '{"cupcake_qty": "bakers dozen"}'

        str_data = json.dumps(data)

        obj = JSONObject(str_data, cast_types=True)

        self.assertIsInstance(obj, JSONObject)
        self.assertEqual(obj.field_embedded, '{"cupcake_qty": "bakers dozen"}')

    def test_list_of_values(self):
        """ Test different values in for a list """
        data = json.loads(self.json_data.simple)
        data['field_list'] = [
            '{"cupcake_qty": "bakers dozen"}',
            'null',
            None
        ]

        str_data = json.dumps(data)

        obj = JSONObject(str_data, cast_types=True)

        self.assertIsInstance(obj, JSONObject)

        self.assertIsInstance(obj.field_list[0], JSONObject)
        self.assertEqual(obj.field_list[0].cupcake_qty, 'bakers dozen')

        self.assertEqual(obj.field_list[1], 'null')
        self.assertIsNone(obj.field_list[2])

