#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Test inherited models and multiple inherited models
#
import base64
import enum
import json
from datetime import datetime, date
from typing import Union, Dict

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


class ForestUploadModel(JSONObject):
    """ Test class for validating an overridden init method """

    body: Union[OakTreeModel, str, bytes, None] = None


    def __init__(self, *args, **kwargs):
        self.method = 'POST'
        self.headers = 'Content-Type: application/json'

        super().__init__(*args, **kwargs)

        def _json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, enum.Enum):
                return obj.value

        if self.body:
            if isinstance(self.body, OakTreeModel):
                self.body = self.body.to_dict(dates_to_str=True)
            if isinstance(self.body, dict):
                self.body = json.dumps(self.body, default=_json_serial)
            if isinstance(self.body, str):
                self.body = base64.b64encode(self.body.encode('utf-8'))


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

    def test_overridden_init_method(self):
        """ Test that an overridden init method works correctly """

        tree_obj = OakTreeModel({
            'id': '50',
            'created': '2023-03-02 19:23:00',
            'modified': '2023-03-02 19:23:00',
            'fall_color': 'Red',
            'lat': '123.123',
            'long': '456.456'}, cast_types=True)

        self.assertIsInstance(tree_obj, OakTreeModel)

        obj = ForestUploadModel({'body': tree_obj})

        self.assertIsInstance(obj.body, bytes)

        # Properties 'method' and 'headers' should exist
        self.assertTrue(hasattr(obj, 'method'))
        self.assertEqual(obj.method, 'POST')

        self.assertTrue(hasattr(obj, 'headers'))
        self.assertEqual(obj.headers, 'Content-Type: application/json')

        # Decode body property
        dec_data_str = base64.b64decode(obj.body).decode('utf-8')

        self.assertIsInstance(dec_data_str, str)
        dec_data = json.loads(dec_data_str)

        self.assertIsInstance(dec_data, dict)
        orig_data = tree_obj.to_dict(dates_to_str=True)
        # Ensure the 'fall_color' Enum object is converted to it's value.
        orig_data['fall_color'] = orig_data['fall_color'].value
        self.assertDictEqual(orig_data, dec_data)

        # Dump data to dictionary and check that all values are present and correct
        data = obj.to_dict(dates_to_str=True)

        self.assertIn('method', data)
        self.assertIn('headers', data)
        self.assertIn('body', data)
