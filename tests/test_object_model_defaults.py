#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from datetime import date, datetime
from enum import Enum, IntEnum

from dateutil import parser as du_parser

from python_easy_json import JSONObject
from tests.base_test import BaseTestCase


class TestEnum(Enum):
    Apple = 1
    Peach = 2
    Orange = 3


class TestIntEnum(IntEnum):
    Lithium = 1
    Iron = 2
    Steel = 3


# A class with some properties with defaults and other without.
class SimpleDefaultsModel(JSONObject):
    field_bool: bool = None
    field_bool_true: bool = True
    field_bool_false: bool = False
    field_int: int = None
    field_int_value: int = 42
    field_float: float = None
    field_float_value: float = 42.0
    field_str: str = None
    field_str_value: str = '42'
    field_date: date = None
    field_date_value: date = date(2023, 1, 1)
    field_datetime: datetime = None
    field_datetime_value: datetime = datetime(2023, 1, 1, 10, 10, 10, 123456)
    field_enum: TestEnum = None
    field_enum_value: TestEnum = TestEnum.Peach
    field_int_enum: TestIntEnum = None
    field_int_enum_value: TestIntEnum = TestIntEnum.Steel


class TestObjectModel(BaseTestCase):
    """ Test using JSONObject for data models """

    def test_simple_model_defaults(self):
        """ Test default values, without passing any data to the JSONObject """

        # Instantiate the SimpleDefaultsModel without any data.
        obj = SimpleDefaultsModel()

        self.assertIsInstance(obj, SimpleDefaultsModel)

        # Check values
        self.assertIsNone(obj.field_bool)
        self.assertTrue(obj.field_bool_true)
        self.assertFalse(obj.field_bool_false)

        self.assertIsNone(obj.field_int)
        self.assertEqual(obj.field_int_value, 42)

        self.assertIsNone(obj.field_float)
        self.assertEqual(obj.field_float_value, 42.0)

        self.assertIsNone(obj.field_str)
        self.assertEqual(obj.field_str_value, '42')

        self.assertIsNone(obj.field_date)
        self.assertEqual(obj.field_date_value, du_parser.parse('2023-01-01').date())

        self.assertIsNone(obj.field_datetime)
        self.assertEqual(obj.field_datetime_value, du_parser.parse('2023-01-01 10:10:10.123456'))

        self.assertIsNone(obj.field_enum)
        self.assertEqual(obj.field_enum_value, TestEnum.Peach)

        self.assertIsNone(obj.field_int_enum)
        self.assertEqual(obj.field_int_enum_value, TestIntEnum.Steel)

    def test_simple_model_export(self):
        """ Test default values when exporting to a dictionary """
        # Instantiate the SimpleDefaultsModel without any data.
        obj = SimpleDefaultsModel()

        self.assertIsInstance(obj, SimpleDefaultsModel)

        # Export the object to a dictionary.
        data = obj.to_dict()

        # Test that all properties WITHOUT a default value are NOT in the dictionary.
        self.assertNotIn('field_bool', data)
        self.assertNotIn('field_int', data)
        self.assertNotIn('field_float', data)
        self.assertNotIn('field_str', data)
        self.assertNotIn('field_date', data)
        self.assertNotIn('field_datetime', data)
        self.assertNotIn('field_field_enum', data)
        self.assertNotIn('field_field_int_enum', data)

        # Test that all properties WITH a default value are IN the dictionary.
        self.assertIn('field_bool_true', data)
        self.assertTrue(data['field_bool_true'])

        self.assertIn('field_bool_false', data)
        self.assertFalse(data['field_bool_false'])

        self.assertIn('field_int_value', data)
        self.assertEqual(data['field_int_value'], 42)

        self.assertIn('field_float_value', data)
        self.assertEqual(data['field_float_value'], 42.0)

        self.assertIn('field_str_value', data)
        self.assertEqual(data['field_str_value'], '42')

        self.assertIn('field_date_value', data)
        self.assertEqual(data['field_date_value'], du_parser.parse('2023-01-01').date())

        self.assertIn('field_datetime_value', data)
        self.assertEqual(data['field_datetime_value'], du_parser.parse('2023-01-01 10:10:10.123456'))

        self.assertIn('field_enum_value', data)
        self.assertEqual(data['field_enum_value'], TestEnum.Peach)

        self.assertIn('field_int_enum_value', data)
        self.assertEqual(data['field_int_enum_value'], TestIntEnum.Steel)

    def test_simple_model_enum_by_key(self):
        """
        Test that the enum property can be set by the Enum key instead of value, when cast_types is True.
        """
        # Instantiate the class with Enum property key names, instead of Enum values.
        obj = SimpleDefaultsModel({'field_enum_value': 'Peach', 'field_int_enum_value': 'Lithium'}, cast_types=True)

        self.assertIsInstance(obj, SimpleDefaultsModel)
        self.assertEqual(obj.field_enum_value, TestEnum.Peach)
        self.assertEqual(obj.field_int_enum_value, TestIntEnum.Lithium)
