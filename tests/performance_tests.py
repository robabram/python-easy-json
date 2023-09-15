#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

# Performance testing the JSONObject
import cProfile

from src.python_easy_json import JSONObject


def run(iterations):

    data = {
        'id': '50',
        'created':'2023-03-02 19:23:00',
        'modified': '2023-03-02 19:23:00',
        'fall_color': 'Red',
        'lat': '123.123',
        'long': '456.456',
        'super_sized': "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    }

    while iterations:

        obj = JSONObject(data)
        data = obj.to_dict()
        iterations -= 1


if __name__ == "__main__":
    cProfile.run('run(100000)')
