#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from typing import Dict, List

from tests.base_test import BaseTestCase
from python_easy_json import JSONObject


class SimpleDictTestObject(JSONObject):

    test_prop: Dict = None


class ListDictTestObject(JSONObject):

    test_prop: List[Dict] = None


class TestListsDict(BaseTestCase):

    def test_simple_dict(self):
        """ Test an object with a typing.Dict type hint.  """

        data = {
            'test_prop': {
                'col1': 'abc',
                'col2': 'xyz'
            }
        }

        obj = SimpleDictTestObject(data, cast_types=True)

        self.assertIsInstance(obj, SimpleDictTestObject)
        # Ensure property type is 'dict'.
        self.assertIsInstance(obj.test_prop, JSONObject)

    def test_list_of_dicts(self):
        """ Test a list of dict objects """
        data = {
            'test_prop': [
                {
                    'col1': 'abc',
                    'col2': 'xyz'
                },
                {
                    'col1': 'ghi',
                    'col2': 'rst'
                }
            ]
        }

        obj = ListDictTestObject(data, cast_types=True)

        self.assertIsInstance(obj, ListDictTestObject)
        # Ensure property type is 'dict'.
        self.assertIsInstance(obj.test_prop, list)

        for v in obj.test_prop:
            self.assertIsInstance(v, JSONObject)

    def test_nested_dict_with_hyphen_key(self):
        """
        Test a key with a hyphen containing a nested dictionary.  Any key with a hyphen should have the hyphen
        converted to an underscore.
        """
        data = {
            'z-report': {
                'zap-col1': 'abc',
                'zap-col2': 'xyz'
            }
        }
        obj = JSONObject(data)

        self.assertIsInstance(obj, JSONObject)
        self.assertTrue(hasattr(obj, 'z_report'))
        self.assertEqual(obj.z_report.zap_col1, 'abc')
