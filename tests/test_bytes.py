#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from tests.base_test import BaseTestCase
from python_easy_json import JSONObject


class TestBytesData(BaseTestCase):

    def test_bytes_data(self):
        """ Test dictionary with bytes data """

        data = {
            'cupcake'.encode('utf-8'): 'bakers dozen'.encode('utf-8')
        }

        obj = JSONObject(data)

        self.assertIsInstance(obj, JSONObject)

        self.assertTrue(hasattr(obj, 'cupcake'))
        self.assertEqual(obj.cupcake, 'bakers dozen')
