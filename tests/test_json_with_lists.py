#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
from typing import List, Optional

from tests.base_test import BaseTestCase
from python_easy_json import JSONObject
from tests.test_object_model import CakeToppingTypeModel


class ListTestObject(JSONObject):

    topping: List[CakeToppingTypeModel]
    string_list: List[str]
    integer_list: List[int]


class TestListsDict(BaseTestCase):

    def test_data_with_lists(self):
        """ Test simple JSON, no type casting. """
        obj = ListTestObject(self.json_data.nested_lists)

        self.assertIsInstance(obj, ListTestObject)

        for t in obj.topping:
            self.assertIsInstance(t, CakeToppingTypeModel)

        for s in obj.string_list:
            self.assertIsInstance(s, str)
            self.assertIn(s, ['abc', 'def', 'xyz'])

        for i in obj.integer_list:
            self.assertIsInstance(i, int)
            self.assertIn(i, [1, 2, 3])

    def test_nested_lists(self):
        """ User supplied unittest for issue #25 """
        class RR(JSONObject):
            values: Optional[list[int]]  # here list is okay

        class P(JSONObject):
            R: List[RR]  # here list cannot be used

        class Q(JSONObject):
            W: List[P]  # and here too

        class P2(JSONObject):
            R: List[RR]  # here list cannot be used

        class Q2(JSONObject):
            W: List[P]  # and here too

        data = json.loads('{"W": [{"R": [{"values": [1, 2, 3]}]}]}')
        # OK
        x = Q(data)
        self.assertIsInstance(x, Q)

        # list() takes no keyword arguments
        data = json.loads('{"W": [{"R": [{"values": [1, 2, 3]}]}]}')
        x2 = Q2(data)
        self.assertIsInstance(x2, Q2)
