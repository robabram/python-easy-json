#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import datetime
import enum
import json
import re
import sys
import typing

from collections import OrderedDict
from dateutil import parser as dt_parser
from json import JSONDecodeError

_enum_t = type(enum.Enum)

# Support OrderedDict for Python versions 3.6 or below.
_OLD_DICT_VERSION = True if sys.version_info.major == 3 and sys.version_info.minor < 7 else False
_REGEX_HIDDEN_PROP = re.compile(r'__')

class JSONObject:
    """
    Simple object to recursively convert a dict or json string to object properties
    """
    # Support OrderedDict for Python versions 3.6 or below.
    __dict_cls__ = OrderedDict if _OLD_DICT_VERSION is True else dict
    __data_dict__ = None  # Holds a clean copy of the data added to this object.

    @staticmethod
    def _get_annot_cls(annots: dict, key: str, ignore_builtins = False) -> typing.List:
        """
        Return defined annotation class if available, otherwise JSONObject class
        :param annots: A compiled set of annotations.
        :param key: Key to lookup in annots.
        :param ignore_builtins: Ignore builtin Python types if Union
        :return: A list of annotation classes or JSONObject class
        """
        cls_types = list()
        if key in annots:
            cls_ = annots[key]
            # See if this annotation is a list of objects, if so, get the first
            # available object type in the list.
            if hasattr(cls_, '_name') and cls_._name == 'List' and hasattr(cls_, '__args__'):
                cls_ = cls_.__args__[0]
            # Check if typing annotation class is a Union type.
            # Try to find the right object class in the Union types list, ignore 'builtin' types.
            if '__args__' in cls_.__dict__ and isinstance(cls_.__dict__['__args__'], (list, tuple)):
                for cls_item in cls_.__dict__['__args__']:
                    # Try to find the right object class in the Union types list, ignore 'builtin' types.
                    if issubclass(type(cls_item), object) and not isinstance(cls_item, typing.TypeVar):
                        if ignore_builtins and cls_item.__module__ == 'builtins':
                            continue
                        cls_types.append(cls_item)
            elif cls_.__module__ == 'typing':
                pass
            else:
                cls_types.append(cls_)

        # Fallback to JSONObject if needed
        if not cls_types:
            cls_types.append(JSONObject)

        return cls_types

    def _collect_annotations(self, cls_: object):
        """
        Recursively collect annotation dictionary values from class and base classes.
        :param cls_: Child object to inspect
        """
        annots = dict()
        if hasattr(cls_, '__bases__') and cls_.__bases__:
            for base in cls_.__bases__:
                if base.__name__ == 'object':
                    continue
                result = self._collect_annotations(base)
                annots.update(result)

        if hasattr(cls_, '__annotations__'):
            annots.update(cls_.__annotations__)

        return annots

    @staticmethod
    def _clean_key(k):
        """ Return a clean key or value """
        if isinstance(k, bytes):
            k = str(k, 'utf-8')
        if '-' in k:
            return k.replace('-', '_')
        return k

    @staticmethod
    def _clean_value(v):
        """ Return a clean key or value """
        if isinstance(v, bytes):
            return str(v, 'utf-8')
        return v

    @classmethod
    def _cast_to_type(cls, annots, k, v):
        """ Try to cast the value to the type"""
        if k not in annots or v is None:
            return v

        # Support Unions types which may have multiple types defined.
        annot_types = cls._get_annot_cls(annots, k)
        # Check to see if the value is already in the correct type.
        if type(v) in annot_types:
            return v

        for t in annot_types:
            if t == datetime.date and not isinstance(v, datetime.date):
                v = dt_parser.parse(str(v)).date()
            elif t == datetime.datetime and not isinstance(v, datetime.datetime):
                v = dt_parser.parse(str(v))
            elif isinstance(t, _enum_t):
                # Try setting the Enum class by value
                try:
                    v = t(v)
                    break
                except ValueError:
                    # try converting type to string and set Enum class by value.
                    try:
                        v = t(str(v))
                        break
                    except ValueError:
                        # Try setting the Enum value by Key instead of value
                        # Hyphens in an enum property is not allowed, convert to underscore.
                        if isinstance(v, str) and '-' in v:
                            v = v.replace('-', '_')
                        v = t[str(v)]
                        break
            else:
                try:
                    v = t(v)
                    break
                except (TypeError, ValueError):
                    pass

        return v

    def __init__(self, data: typing.Union[typing.Dict, str, None] = None, cast_types: bool = False,
                 ordered: bool = False):
        """
        Load the dictionary or JSON string data argument into ourselves as properties.
        :param data: Dictionary or valid JSON string.
        :param cast_types: If properties of this class are type annotated, try to cast them.
        :param ordered: Use OrderedDict() if set, otherwise use dict().
        """
        # 'self.__data_dict__' may have data already due to self.__setattr__ being called before reaching here.
        if self.__data_dict__ is None:
            self.__data_dict__ = self.__dict_cls__()

        if isinstance(data, str):
            data = json.loads(data)

        # Collect the class annotations, along with any base class annotations.
        annots = self._collect_annotations(self.__class__)
        # List of keys in the data which contain nested data, IE: list or dict objects.
        if data:
            self.__nested_keys__ = [self._clean_key(k) for k in data.keys() if isinstance(data[k], (dict, list))]
            # Ensure keys and values are not byte strings and ensure keys value may be used as a property.
            for k, v in data.items():
                self.__data_dict__[self._clean_key(k)] = self._clean_value(v)
        else:
            # cleaned_data = self.__dict_cls__()
            self.__nested_keys__ = self.__dict_cls__()

        if annots:
            if cast_types is True:
                # If 'cast_types' is True, try to cast values to correct type.
                for k in self.__data_dict__.keys():
                    if k in self.__nested_keys__:
                        continue
                    # Attempt to cast the value to the annotation type
                    self.__data_dict__[k] = self._cast_to_type(annots, k, self.__data_dict__[k])

            # Set default values for any keys that are missing in the 'data' dict.
            for k in annots.keys():
                if k in self.__class__.__dict__:
                    v = getattr(self.__class__, k)
                    # Only set default values that are not None
                    if k not in self.__data_dict__ and v is not None:
                        self.__data_dict__[k] = v

        # If there are any nested keys, recursively process them.
        for k in self.__nested_keys__:
            # Fetch annotation class type or JSONObject
            t = self._get_annot_cls(annots, k, ignore_builtins=True)[0]

            if isinstance(self.__data_dict__[k], dict):
                self.__data_dict__[k] = t(self.__data_dict__[k], cast_types=cast_types, ordered=ordered)
            elif isinstance(self.__data_dict__[k], list):
                _tmp = list()
                for i in self.__data_dict__[k]:
                    if isinstance(i, dict):
                        _tmp.append(t(i, cast_types=cast_types, ordered=ordered))
                    elif isinstance(i, str):
                        try:
                            _tmp_data = json.loads(i)
                            if _tmp_data and isinstance(_tmp_data, dict):
                                _tmp.append(t(_tmp_data, cast_types=cast_types, ordered=ordered))
                            else:
                                _tmp.append(i)  # For when the value is a string = 'null'.
                        except JSONDecodeError:
                            _tmp.append(i)
                    else:
                        _tmp.append(i)
                self.__data_dict__[k] = _tmp

        # Save data to the object properties
        for k, v in self.__data_dict__.items():
            self.__dict__[k] = v

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        # Regex search is slightly faster than 'key.startswith()'.
        if _REGEX_HIDDEN_PROP.search(key):
            return
        # If we are here and self.__data_dict__ is None, we should initialize it and store the value. This
        # probably means the __init__() method has been overridden and we are still waiting for our __init__()
        # method to be called.
        if not self.__data_dict__:
            self.__data_dict__ = self.__dict_cls__()
        self.__data_dict__[key] = value

    @staticmethod
    def _json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return obj.__repr__()

    def to_json(self, indent: int = None):
        """
        Export stored data as a json string.
        :param indent: Positive integer value for formatting JSON string indenting.
        """
        return json.dumps(self.__data_dict__, default=self._json_serial, indent=indent)

    def to_dict(self, recursive: bool = True, dates_to_str: bool = False):
        """
        Export stored data as a python dictionary object.
        :param recursive: Boolean, recursively convert nested JSONObjects to a dict
        :param dates_to_str: Boolean, convert all date or datetime values to string.
        """
        data = self.__dict_cls__()

        for k, v in self.__data_dict__.items():
            if isinstance(v, JSONObject) and recursive is True:
                data[k] = v.to_dict(recursive=recursive, dates_to_str=dates_to_str)
            elif isinstance(v, (datetime.datetime, datetime.date)) and dates_to_str is True:
                data[k] = self._json_serial(v)
            elif isinstance(v, list):
                nl = list()
                for i in v:
                    if isinstance(i, JSONObject) and recursive is True:
                        nl.append(i.to_dict(recursive=recursive, dates_to_str=dates_to_str))
                    else:
                        nl.append(i)
                data[k] = nl
            else:
                data[k] = v

        return data

    def __repr__(self):
        return self.to_json()
