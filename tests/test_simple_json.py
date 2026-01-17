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

    def test_update_with_dict(self):
        """ Test we can update the JSONObject by passing a dict object """
        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        obj = obj.update({'test_prop': 456, 'new_prop': 987})

        self.assertEqual(obj.new_prop, 987)
        self.assertEqual(obj.test_prop, 456)

        data = obj.to_dict()

        self.assertEqual(data['new_prop'], 987)
        self.assertEqual(data['test_prop'], 456)

    def test_update_with_keyword_args(self):
        """ Test we can update the JSONObject by passing key word arguments """
        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        obj = obj.update(test_prop=456, new_prop=987)

        self.assertEqual(obj.new_prop, 987)
        self.assertEqual(obj.test_prop, 456)

        data = obj.to_dict()

        self.assertEqual(data['new_prop'], 987)
        self.assertEqual(data['test_prop'], 456)

    def test_update_with_iterable_pairs(self):
        """ Test we can update the JSONObject by passing iterable pair arguments """
        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        obj = obj.update([('test_prop', 456), ('new_prop', 987)])

        self.assertEqual(obj.new_prop, 987)
        self.assertEqual(obj.test_prop, 456)

        data = obj.to_dict()

        self.assertEqual(data['new_prop'], 987)
        self.assertEqual(data['test_prop'], 456)

    def test_update_exceptions(self):
        """ Test update using bad data to cause exceptions """

        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        # Test no args, should not raise an error.
        self.assertIsInstance(obj.update({}), JSONObject)

        # Test non-iterable value raises TypeError
        self.assertRaises(TypeError, obj.update, None)
        self.assertRaises(TypeError, obj.update, 123)

        # Test bad iterable pair raise ValueError
        self.assertRaises(ValueError, obj.update, [('test_prop', 456, 333)])

    def test_number_of_properties(self):
        """ Test the number of properties by calling len() function """

        obj = JSONObject({'test_prop': 123, 'another_prop': 'abc'})
        self.assertIsInstance(obj, JSONObject)

        self.assertEqual(len(obj), 2)

    def test_add_object(self):
        """ Test add object """
        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        other_obj = JSONObject({'another_prop': 'abc'})
        self.assertIsInstance(other_obj, JSONObject)

        island_other_obj = JSONObject({'island_prop': 'sandy'})
        self.assertIsInstance(island_other_obj, JSONObject)

        obj += other_obj

        self.assertEqual(obj.test_prop, 123)
        self.assertEqual(obj.another_prop, 'abc')

        obj = obj + island_other_obj

        self.assertEqual(obj.island_prop, 'sandy')

    def test_add_invalid_operand(self):
        """ Test adding an invalid operand """
        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        try:
            obj += {'other_prop': 'abc'}
        except TypeError:
            pass

        self.assertFalse(hasattr(obj, 'other_prop'))

    def test_cast_to_dict(self):
        """ Test cast a JSONObject to a dict """
        obj = JSONObject({'test_prop': 123})
        self.assertIsInstance(obj, JSONObject)

        dict1 = dict(obj)
        dict2 = obj.to_dict(dates_to_str=True)
        self.assertEqual(dict1, dict2)
