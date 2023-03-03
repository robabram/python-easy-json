#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Test inherited models and multiple inherited models
#

from datetime import datetime
from dateutil import parser as du_parser
from enum import Enum

from python_easy_json import JSONObject
from tests.base_test import BaseTestCase


class FallColors(Enum):
    Red = 1
    Orange = 2
    Mixed = 3


class BaseModel(JSONObject):
    id: int
    created: datetime
    modified: datetime


class PlantModel(BaseModel):
    species: str
    lat: float
    long: float


class DeciduousModelMixin(JSONObject):
    height: float
    diameter: float
    flowering: bool
    fall_color: FallColors


class SoilModelMixin(JSONObject):
    soil_type: str = None


class OakTreeModel(PlantModel, DeciduousModelMixin, SoilModelMixin):
    species: str = 'Oak Tree'
    flowering: bool = False



class TestListsDict(BaseTestCase):

    def test_simple_inherited_model(self):
        """ Test a class based on a parent class """
        obj = PlantModel({
            'id': '10',
            'created': '2023-03-02 19:23:00',
            'modified': '2023-03-02 19:23:00',
            'species': 'Test Shrub'}, cast_types=True)

        self.assertIsInstance(obj, PlantModel)

        self.assertEqual(obj.id, 10)
        self.assertEqual(obj.created, du_parser.parse('2023-03-02 19:23:00'))
        self.assertEqual(obj.modified, du_parser.parse('2023-03-02 19:23:00'))
        self.assertEqual(obj.species, 'Test Shrub')

    def test_multiple_inherited_models(self):
        """ Test a class based on multiple parent classes and casting types """
        obj = OakTreeModel({
            'id': '50',
            'created': '2023-03-02 19:23:00',
            'modified': '2023-03-02 19:23:00',
            'fall_color': 'Red',
            'lat': '123.123',
            'long': '456.456'}, cast_types=True)

        self.assertIsInstance(obj, OakTreeModel)

        self.assertEqual(obj.id, 50)
        self.assertEqual(obj.created, du_parser.parse('2023-03-02 19:23:00'))
        self.assertEqual(obj.modified, du_parser.parse('2023-03-02 19:23:00'))
        self.assertEqual(obj.species, 'Oak Tree')

        self.assertIsInstance(obj.fall_color, FallColors)
        self.assertEqual(obj.fall_color, FallColors.Red)

        self.assertEqual(obj.lat, 123.123)
        self.assertEqual(obj.long, 456.456)

        self.assertEqual(obj.flowering, False)

        # Test default value of None
        self.assertIsNone(obj.soil_type)
