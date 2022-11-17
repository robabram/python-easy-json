#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from typing import List

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
