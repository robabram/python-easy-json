#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
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

