**********************************************************************************
JSONObject: simple, yet powerful, JSON/python dictionary to object deserialization  
**********************************************************************************

**JSONObject** is a recursive JSON to python object deserializer with support for defining data models and casting data to python using type hint annotations. 

The python-json-object can be used to:

- **Deserialize:** Recursively convert a JSON string or python dictionary to a python object
- **Serialize:** Export the object data to a JSON string or python dictionary
- **Define Data Models:** Create simple, yet powerful data models for working with data from any source
- **IDE Auto Completion:** IDEs with auto-completion and support python type hinting will auto-complete model properties
- **Type Casting:** Convert JSON values to specific types by creating models and type hints.
- **Hashing:** Repeatable hashing algorithm allows easy data comparisons


Get It Now
==========

    Too many like named projects on PyPi.  Need to find a new package name.

Why a JSON Object library?
==========================
After years of python development, I grew tired of receiving data from APIs, database, csv files and so on and working with them as python dictionaries. IE: 

    for row in results:
        if row['the_key'][0]['another_key'] == 'the_value':
            ...

With JSONObject this may be re-written as:

    from json_object import JSONObject

    for row in [JSONObject(r) for r in results]:
        if row.the_key[0].another_key == 'the_value':
            ...

Which makes the code more readable and less cluttered when dealing with complex dictionary structures in code.


Simple Examples
===============

Data from a JSON String

    from json_object import JSONObject
    
    # JSON string
    obj = JSONObject('{"test_key": "test_value"}')
    print(obj.to_json())

    $ {"test_key": "test_value"}

Data from a python dictionary

    # Python dictionary 
    obj = JSONObject({'test_key': 'test_value'})
    print(obj.to_json())

    $ {"test_key": "test_value"}


Data Models For Anything
========================

Using JSONObject, you can create data models, including deeply nested models and arrays, from any JSON or dictionary. Additionally, python type hinting can be used to cast values to the type defined by the type hints.

As a bonus, IDEs with auto-completion and support python type hinting will auto-complete model properties as you type. 

This example shows how to define nested/child data models, including lists of data models.

    # Represents json from 'tests/test_data/nested_data_1.json'
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

    cake = CakeModel(data)
    print(f'Cake: {cake.name} ({len(cake.batters.batter)} ingredents).') 

    $ Cake: Devil's Food Cake (4 ingredents).


Automatically Convert JSON Values
=================================
If a model has been defined and the properties have python type hint annotations, the JSONObject can convert values to the annotation type.

    from datetime import datetime 

    class TimestampModel(JSONObject):
        id: int = None
        timestamp: datetime = None

    data = {'id': "123", "timestamp": "2022-09-19 10:11:01.123456"}
    obj = TimestampModel(data, cast_types=True)

    if obj.id > 0:
        print(f"ID: {obj.id}: {obj.timestamp.strftime('%b %d, %Y @ %H:%M:%S %p')}")

    $ ID: 123: Sep 19, 2022 @ 10:11:01 AM

    
Project Links
=============

- PyPI: https://pypi.python.org/pypi/python-json-object
- Issues: https://github.com/robabram/Python-JSONObject/issues

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/robabram/Python-JSONObject/blob/main/LICENSE>`_ file for more details.


Test Data
=========

Test data for examples and unittests sourced from: https://opensource.adobe.com/Spry/samples/data_region/JSONDataSetSample.html