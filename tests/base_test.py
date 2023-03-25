#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import os
import glob

from unittest import TestCase

from python_easy_json import JSONObject


class BaseTestCase(TestCase):
    """ Base class for all unittests """
    # A dictionary of test JSON data from the 'tests/test_data' directory.  The file name, minus extension,
    # becomes the dictionary key id.
    json_data: JSONObject = None

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        # Current directory should be project root directory.
        cur_dir = os.path.abspath(os.path.curdir)
        test_data_dir = os.path.join(cur_dir, "tests/test_data")
        files = glob.glob(os.path.join(test_data_dir, "*.json"))

        data = dict()
        for file in files:
            key = os.path.basename(file).split('.')[0]
            data[key] = open(file).read()
        # Convert the json file data we just loaded into a JSONObject.
        self.json_data = JSONObject(data)
