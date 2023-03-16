#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from datetime import date, datetime
from dateutil import parser as du_parser
import json
from python_easy_json import JSONObject
from tests.base_test import BaseTestCase
from typing import List, Union, Optional


# Represent the test_data/simple.json
class SimpleModel(JSONObject):
    field_bool: bool = None
    field_int: int = None
    field_float: float = None
    field_str: str = None
    field_date: date = None
    field_datetime: datetime = None


# Represent test_data/nested_data_1.json as data models
class CakeToppingTypeModel(JSONObject):
    id: int = None
    type: str = None


class CakeBatterTypeModel(JSONObject):
    id: int = None
    type: str = None


class CakeBatterModel(JSONObject):
    batter: List[CakeBatterTypeModel] = None


class CakeModel(JSONObject):
    id: str = None
    type: str = None
    name: str = None
    ppu: float = None
    batters: CakeBatterModel = None
    topping: List[CakeToppingTypeModel]


class IncompleteCakeModel(CakeModel):
    # Force topping to just be a plain list.
    topping: List = None


class PythonTypingUnionModel(JSONObject):
    # Test that Union type hints work correctly.
    data: Union[str, int, CakeModel] = None
    platform: Optional[CakeBatterTypeModel] = None
    settings: Optional[JSONObject] = None


class TestObjectModel(BaseTestCase):
    """ Test using JSONObject for data models """

    def test_simple_model(self):
        """ Test the simple JSON model, do not cast values to annotation types. """
        obj = SimpleModel(self.json_data.simple)

        self.assertIsInstance(obj, SimpleModel)
        self.assertNotIsInstance(obj, CakeModel)

        # Check value types have not been converted to annotation types.
        self.assertIsInstance(obj.field_bool, str)
        self.assertIsInstance(obj.field_int, int)
        self.assertIsInstance(obj.field_float, float)
        self.assertIsInstance(obj.field_date, str)
        self.assertIsInstance(obj.field_datetime, str)

        # Check values
        self.assertEqual(obj.field_bool, 'true')
        self.assertEqual(obj.field_int, 123)
        self.assertEqual(obj.field_float, 456.789)
        self.assertEqual(obj.field_date, '2022-09-09')
        self.assertEqual(obj.field_datetime, '2022-09-19 10:11:01.123456')

    def test_simple_model_cast_types(self):
        """ Test the simple JSON model, cast values to annotation types. """
        obj = SimpleModel(self.json_data.simple, cast_types=True)

        self.assertIsInstance(obj, SimpleModel)
        self.assertNotIsInstance(obj, CakeModel)

        # Check value types have not been converted to annotation types.
        self.assertIsInstance(obj.field_bool, bool)
        self.assertIsInstance(obj.field_int, int)
        self.assertIsInstance(obj.field_float, float)
        self.assertIsInstance(obj.field_date, date)
        self.assertIsInstance(obj.field_datetime, datetime)

        # Check values
        self.assertEqual(obj.field_bool, True)
        self.assertEqual(obj.field_int, 123)
        self.assertEqual(obj.field_float, 456.789)
        self.assertEqual(obj.field_date.strftime('%Y-%m-%d'), '2022-09-09')
        self.assertEqual(obj.field_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'), '2022-09-19 10:11:01.123456')

    def test_cake_models(self):
        """ Test JSONObject CakeModel model, do not cast values to annotation types. """
        obj = CakeModel(self.json_data.nested_data_1)

        self.assertIsInstance(obj, CakeModel)
        self.assertIsInstance(obj.topping, list)

        self.assertIsInstance(obj.batters, CakeBatterModel)
        self.assertIsInstance(obj.batters.batter, List)
        self.assertIsInstance(obj.batters.batter[0], CakeBatterTypeModel)

        # Check that types were not converted to the property annotation type.
        self.assertIsInstance(obj.batters.batter[0].id, str)
        self.assertEqual(obj.batters.batter[0].id, '1001')
        self.assertEqual(obj.batters.batter[0].type, 'Regular')

        self.assertIsInstance(obj.topping[0], CakeToppingTypeModel)

        # Check that types were not converted to the property annotation type.
        self.assertIsInstance(obj.topping[0].id, str)
        self.assertEqual(obj.topping[0].id, '5001')
        self.assertEqual(obj.topping[0].type, 'None')

    def test_cake_models_convert_types(self):
        """ Test JSONObject CakeModel model, casting values to annotation types. """
        obj = CakeModel(self.json_data.nested_data_1, cast_types=True)

        self.assertIsInstance(obj, CakeModel)
        self.assertIsInstance(obj.topping, list)

        self.assertIsInstance(obj.batters, CakeBatterModel)
        self.assertIsInstance(obj.batters.batter, List)
        self.assertIsInstance(obj.batters.batter[0], CakeBatterTypeModel)

        # Check that types were converted to the property annotation type.
        self.assertIsInstance(obj.batters.batter[0].id, int)
        self.assertEqual(obj.batters.batter[0].id, 1001)

        self.assertIsInstance(obj.topping[0], CakeToppingTypeModel)

        # Check that types were converted to the property annotation type.
        self.assertIsInstance(obj.topping[0].id, int)
        self.assertEqual(obj.topping[0].id, 5001)

    def test_cake_model_lists(self):
        """ Test the length of the lists in the Cake model. """
        obj = CakeModel(self.json_data.nested_data_1, cast_types=True)

        self.assertIsInstance(obj, CakeModel)
        self.assertIsInstance(obj.topping, list)
        self.assertIsInstance(obj.batters.batter, List)

        self.assertEqual(len(obj.topping), 7)
        self.assertEqual(len(obj.batters.batter), 4)

    def test_incomplete_cake_models(self):
        """ Test an incomplete annotated CakeModel model, test incomplete annotations for nested objects. """
        obj = IncompleteCakeModel(self.json_data.nested_data_1)

        self.assertIsInstance(obj, IncompleteCakeModel)
        self.assertIsInstance(obj.topping, list)
        self.assertIsInstance(obj.topping[0], JSONObject)

        # Check that types were *NOT* converted to the property annotation type, because the type annotations
        # are missing in this case.
        self.assertIsInstance(obj.topping[0].id, str)
        self.assertEqual(obj.topping[0].id, "5001")

    def test_to_dict_datetime_conversion(self):
        """ Test that when using the "to_dict()" method that datetime values are handled correctly. """

        input_ = json.loads(self.json_data.simple)
        input_['field_date'] = du_parser.parse(input_['field_date']).date()
        input_['field_datetime'] = du_parser.parse(input_['field_datetime'])

        obj = SimpleModel(input_)

        # Test that date and datetime values are not converted to string
        data = obj.to_dict(dates_to_str=False)
        self.assertIsInstance(data['field_date'], date)
        self.assertIsInstance(data['field_datetime'], datetime)

        data = obj.to_dict(dates_to_str=True)
        self.assertIsInstance(data['field_date'], str)
        self.assertIsInstance(data['field_datetime'], str)

    def test_typing_union(self):
        """ Test that properties annotated with Union work correctly when they include a JSONObject """

        # Test string value in Union property
        input_ = {
            'data': 'No Data',
            'platform': None
        }

        obj = PythonTypingUnionModel(input_, cast_types=True)

        self.assertEqual(obj.data, 'No Data')
        self.assertIsInstance(obj.data, str)

        # Test integer value in Union property
        input_['data'] = 20

        obj = PythonTypingUnionModel(input_, cast_types=True)

        self.assertEqual(obj.data, 20)

        # Test CakeModel object in Union property
        input_['data'] = {'id': 1, 'type': 'bunt'}

        obj = PythonTypingUnionModel(input_, cast_types=True)

        self.assertIsInstance(obj.data, CakeModel)
        self.assertEqual(obj.data.id, '1')
        self.assertEqual(obj.data.type, 'bunt')

    def test_typing_optional(self):
        """ Test that properties annotated with Optional work correctly when they include a JSONObject """

        # Test None value in Optional properties
        input_ = {
            'data': 'No Data',
            'platform': None,
            'settings': None
        }

        obj = PythonTypingUnionModel(input_, cast_types=True)

        self.assertEqual(obj.data, 'No Data')

        self.assertIsNone(obj.platform)
        self.assertIsNone(obj.settings)

        # Test dict value in Optional properties
        input_ = {
            'data': 'No Data',
            'platform': {'id': 1, 'type': 'bunt'},
            'settings': {'temp': 250.0, 'time': 45.0}
        }

        obj = PythonTypingUnionModel(input_, cast_types=True)
        self.assertIsInstance(obj.platform, CakeBatterTypeModel)

        # Test subclass of JSONObject
        self.assertEqual(obj.platform.id, 1)
        self.assertEqual(obj.platform.type, 'bunt')
        # Test JSONObject class
        self.assertEqual(obj.settings.temp, 250.0)
        self.assertEqual(obj.settings.time, 45.0)
