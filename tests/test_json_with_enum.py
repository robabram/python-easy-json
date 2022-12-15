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


class TestIntEnum(IntEnum):

    FirstValue = 1
    SecondValue = 2


class ObjectWithEnum(JSONObject):
    """ JSONObject object class with Enum types """
    timestamp: datetime = None
    test_enum: TestEnum = None
    test_int_enum: TestIntEnum = None


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
