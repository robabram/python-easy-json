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

    def test_property_set_after_init(self):
        """ Test additional property setting is recorded after the object is initialized """
        obj = JSONObject({'prop_abc': None})

        self.assertIsInstance(obj, JSONObject)

        self.assertIsNone(obj.prop_abc)
        data = obj.to_dict()
        self.assertIsNone(data['prop_abc'])

        obj.prop_abc = '123'

        self.assertEqual(obj.prop_abc, '123')
        data = obj.to_dict()
        self.assertEqual(data['prop_abc'], '123')

    def test_setting_object_after_init(self):
        """ Test setting a nested object after init """

        obj = JSONObject({'prop_obj': None})

        nested_obj = JSONObject({'nested_prop': 123})

        self.assertIsInstance(obj, JSONObject)
        self.assertIsInstance(nested_obj, JSONObject)

        obj.prop_obj = nested_obj

        data = obj.to_dict()
        self.assertIsInstance(data['prop_obj'], dict)
        self.assertEqual(data['prop_obj']['nested_prop'], 123)

    def test_property_with_single_hyphen(self):

        obj = JSONObject({'_test_prop': 123})

        self.assertIsInstance(obj, JSONObject)
        self.assertEqual(obj._test_prop, 123)

        data = obj.to_dict()
        self.assertEqual(data['_test_prop'], 123)

    def test_setattr_after_init(self):
        """ Test that calling setattr() works correctly after init """

        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        setattr(obj, 'new_prop', 'abc')
        self.assertEqual(obj.new_prop, 'abc')

        data = obj.to_dict()
        self.assertEqual(data['new_prop'], 'abc')
        self.assertEqual(data['test_prop'], 123)
