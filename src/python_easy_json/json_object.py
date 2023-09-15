#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import copy
import datetime
import enum
import json
import typing

from collections import OrderedDict
from dateutil import parser as dt_parser
from json import JSONDecodeError

_enum_t = type(enum.Enum)


class JSONObject:
    """
    Simple object to recursively convert a dict or json string to object properties
    """
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
        cls_ = None
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
                    if issubclass(type(cls_item), object):
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
        return k.replace('-', '_')

    @staticmethod
    def _clean_value(v):
        """ Return a clean key or value """
        if isinstance(v, bytes):
            v = str(v, 'utf-8')
        return v

    @classmethod
    def _cast_to_type(cls, annots, k, v):
        """ Try to cast the value to the type"""
        if k not in annots or v is None:
            return v

        # Support Unions types which may have multiple types defined.
        annot_types = cls._get_annot_cls(annots, k)
        # Check to see if the value is already in the correct type.
        for t in annot_types:
            if type(v) == t:
                return v

        for t in annot_types:
            try:
                if t == datetime.date and not isinstance(v, datetime.date):
                    v = dt_parser.parse(str(v)).date()
                elif t == datetime.datetime and not isinstance(v, datetime.datetime):
                    v = dt_parser.parse(str(v))
                elif isinstance(t, _enum_t):
                    # Try setting the Enum class by value
                    try:
                        v = t(str(v))
                        break
                    except ValueError:
                        # try original type in case annotation type is an Enum and value is an integer.
                        try:
                            v = t(v)
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
                    except (json.decoder.JSONDecodeError, ValueError, TypeError):
                        continue
            except TypeError:
                continue

        return v


    def __init__(self, data: typing.Union[typing.Dict, str, None] = None, cast_types: bool = False,
                 ordered: bool = False):
        """
        Load the dictionary or JSON string data argument into ourselves as properties.
        :param data: Dictionary or valid JSON string.
        :param cast_types: If properties of this class are type annotated, try to cast them.
        :param ordered: Use OrderedDict() if set, otherwise use dict().
        """
        # # Support OrderedDict for Python versions 3.6 or below.
        # self.__data_dict__ = dict() if not ordered else OrderedDict()
        self.__data_dict__: typing.Dict = dict()
        # List of keys in the data which contain nested data, IE: list or dict objects.
        self.__nested_keys__: typing.List[str] = None  # Is there any nested data

        if isinstance(data, str):
            data = json.loads(data)
        if not data:
            data = dict()

        cleaned_data = dict() if not ordered else OrderedDict()

        # Inspect the class
        meta: typing.Dict = dict(vars(self.__class__))
        # Collect the class annotations, along with any base class annotations.
        annots: typing.Dict = self._collect_annotations(self.__class__)
        self.__nested_keys__ = [k for k in data.keys() if isinstance(data[k], (dict, list))] if data else dict()

        # Ensure keys and values are not byte strings.
        if data:
            cleaned_data.update({self._clean_key(k): self._clean_value(v) for k, v in data.items()})

        # If there are no annotations and no nested data, just set the class dict property and return.
        if not annots and not self.__nested_keys__:
            if cleaned_data:
                for k, v in cleaned_data.items():
                    self.__dict__[k] = v
                self.__data_dict__ = cleaned_data
            return

        if annots:
            if cast_types is True:
                # If 'cast_types' is True, try to cast values to correct type.
                for k in cleaned_data.keys():
                    if k in self.__nested_keys__:
                        continue
                    # Attempt to cast the value to the annotation type
                    cleaned_data[k] = self._cast_to_type(annots, k, cleaned_data[k])

            # Set default values for any keys that are missing in the 'data' dict.
            for k in annots.keys():
                if k in self.__class__.__dict__:
                    v = getattr(self.__class__, k)
                    # Only set default values that are not None
                    if k not in cleaned_data and v is not None:
                        cleaned_data[k] = v

        # If there are any nested keys, recursively process them.
        for k in self.__nested_keys__:
            if k not in cleaned_data:
                continue
            # Fetch annotation class type or JSONObject
            t = self._get_annot_cls(annots, k, ignore_builtins=True)[0]

            if isinstance(cleaned_data[k], dict):
                cleaned_data[k] = t(cleaned_data[k], cast_types=cast_types, ordered=ordered)
            elif isinstance(cleaned_data[k], list):
                _tmp = list()
                for i in cleaned_data[k]:
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
                cleaned_data[k] = _tmp

        # Update class properties and save the data
        for k, v in cleaned_data.items():
            self.__dict__[k] = v
        self.__data_dict__ = cleaned_data

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
        data = dict()

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
