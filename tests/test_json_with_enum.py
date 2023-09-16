#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from datetime import datetime
from enum import Enum, IntEnum

from tests.base_test import BaseTestCase
from python_easy_json import JSONObject


class TestEnum(Enum):
    FirstValue = 1
    SecondValue = 2


class TestStrEnum(str, Enum):
    FirstStrValue = "10"
    SecondStrValue = "20"

class TestIntEnum(IntEnum):
    FirstValue = 1
    SecondValue = 2


class TestUnderscoreEnum(Enum):
    data_with_hyphen = 1


class ObjectWithEnum(JSONObject):
    """ JSONObject object class with Enum types """
    timestamp: datetime = None
    test_enum: TestEnum = None
    test_int_enum: TestIntEnum = None
    underscore_enum: TestUnderscoreEnum = None


class ObjectWithStrEnum(JSONObject):
    """ JSONObject object class with Enum types """
    timestamp: datetime = None
    test_enum: TestStrEnum = None
    test_int_enum: TestStrEnum = None

class TestJSONWithEnum(BaseTestCase):

    def test_object_with_enum_values(self):
        """ Test JSONObject class with IntEnum property. """
        ts = datetime.utcnow()

        data = {
            'timestamp': ts.isoformat(),
            'test_enum': TestEnum.FirstValue.value,
            'test_int_enum': TestIntEnum.SecondValue.value
        }

        obj = ObjectWithEnum(data, cast_types=True)

        self.assertIsInstance(obj, JSONObject)

        self.assertEqual(obj.timestamp, ts)

        # TestEnum
        self.assertIsInstance(obj.test_enum, TestEnum)
        self.assertEqual(obj.test_enum, TestEnum.FirstValue)

        # TestIntEnum
        self.assertIsInstance(obj.test_int_enum, TestIntEnum)
        self.assertEqual(obj.test_int_enum, TestIntEnum.SecondValue)

    def test_str_enum(self):
        """ Test an enum with string values """
        ts = datetime.utcnow()

        data = {
            'timestamp': ts.isoformat(),
            'test_enum': TestStrEnum.FirstStrValue.value,
            'test_int_enum': int(TestStrEnum.SecondStrValue.value)
        }

        obj = ObjectWithStrEnum(data, cast_types=True)

        self.assertIsInstance(obj, JSONObject)

        # TestEnum
        self.assertIsInstance(obj.test_enum, TestStrEnum)
        self.assertEqual(obj.test_enum, TestStrEnum.FirstStrValue)

        # TestIntEnum
        self.assertIsInstance(obj.test_int_enum, TestStrEnum)
        self.assertEqual(obj.test_int_enum, TestStrEnum.SecondStrValue)

    def test_enum_with_hyphen_key(self):
        """
        Test case where the data value for an enum value has a hyphen in it.
        """
        data = {
            'underscore_enum': 'data-with-hyphen'
        }

        obj = ObjectWithEnum(data, cast_types=True)

        self.assertIsInstance(obj, JSONObject)

        self.assertEqual(obj.underscore_enum, TestUnderscoreEnum.data_with_hyphen)
