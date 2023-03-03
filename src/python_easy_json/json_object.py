#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import datetime
import json
import inspect

from collections import OrderedDict
from dateutil import parser as dt_parser
from json import JSONDecodeError
from typing import Dict, Union


class JSONObject:
    """
    Simple object to recursively convert a dict or json string to object properties
    """
    __data_dict__ = None

    @staticmethod
    def _get_annot_cls(annots: dict, key: str):
        """
        Return defined annotation class if available, otherwise JSONObject class
        :param annots: A compiled set of annotations.
        :param key: Key to lookup in annots.
        :return: Annotation class or JSONObject class
        """
        cls_ = JSONObject
        if key in annots:
            cls_ = annots[key]
            # See if this annotation is a list of objects, if so, get the first
            # available object type in the list.
            if hasattr(cls_, '_name') and cls_._name == 'List':
                try:
                    cls_ = cls_.__args__[0]
                except AttributeError:
                    pass
        return cls_

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


    def __init__(self, data: Union[Dict, str, None] = None, cast_types: bool = False, ordered: bool = False):
        """
        Load the dictionary or JSON string data argument into ourselves as properties.
        :param data: Dictionary or valid JSON string.
        :param cast_types: If properties of this class are type annotated, try to cast them.
        :param ordered: Use OrderedDict() if set, otherwise use dict().
        """
        # Support OrderedDict for Python versions 3.6 or below.
        self.__data_dict__ = dict() if not ordered else OrderedDict()

        if isinstance(data, str):
            data = json.loads(data)

        # Compile the class annotations, along with any base class annotations.
        annots = self._collect_annotations(self.__class__)

        _cleaned_data = None
        if data:
            _cleaned_data = dict() if not ordered else OrderedDict()
            for k, v in data.items():
                # Convert bytes to str
                if isinstance(k, bytes):
                    k = str(k, 'utf-8')
                if isinstance(v, bytes):
                    v = str(v, 'utf-8')
                k = k.replace('-', '_')  # Convert key names to python class property friendly name.
                _cleaned_data[k] = v
                if isinstance(v, dict):
                    self.__dict__[k] = self._get_annot_cls(annots, k)(v, cast_types=cast_types, ordered=ordered)
                elif isinstance(v, list):
                    _tmp = list()
                    for i in v:
                        if isinstance(i, dict):
                            try:
                                _tmp.append(self._get_annot_cls(annots, k)(i, cast_types=cast_types, ordered=ordered))
                            except TypeError:
                                _tmp.append(JSONObject(i, cast_types=cast_types, ordered=ordered))
                        elif isinstance(i, str):
                            try:
                                _tmp_data = json.loads(i)
                                if _tmp_data and isinstance(_tmp_data, dict):
                                    _tmp.append(self._get_annot_cls(annots, k)(_tmp_data, cast_types=cast_types,
                                                                       ordered=ordered))
                                else:
                                    _tmp.append(i)  # For when the value is a string = 'null'.
                            except JSONDecodeError:
                                _tmp.append(i)
                        else:
                            _tmp.append(i)
                    self.__dict__[k] = _tmp
                else:
                    self.__dict__[k] = v
                    # Try to cast values to annotation type if type annotation have been set.
                    if cast_types is True and k in annots:
                        try:
                            if annots[k] == datetime.date:
                                self.__dict__[k] = dt_parser.parse(str(v)).date()
                            elif annots[k] == datetime.datetime:
                                self.__dict__[k] = dt_parser.parse(str(v))
                            else:
                                # Try setting the Enum class by value
                                try:
                                    self.__dict__[k] = annots[k](str(v))
                                except ValueError:
                                    # try original type in case annotation type is an Enum and value is an integer.
                                    try:
                                        self.__dict__[k] = annots[k](v)
                                    except ValueError:
                                        # Try setting the Enum value by Key instead of value
                                        self.__dict__[k] = annots[k][str(v)]
                        except TypeError:
                            pass
                        except ValueError:
                            pass

        # Look for any properties that have a default value on the class, but were not in the 'data' argument.
        members = dict(inspect.getmembers(self.__class__, lambda a: not inspect.isroutine(a)))
        for k, v in members.items():
            if k.startswith('_'):
                continue
            if k not in self.__dict__ and hasattr(self, k) and getattr(self, k) is not None:
                self.__dict__[k] = v

        if _cleaned_data:
            self._clean_data()

    def _clean_data(self):
        """ Take the class __dict__ and update the self.__data_dict__ and self.__data_str__ values. """
        for k, v in self.__dict__.items():
            if k is None or k.startswith('__'):
                continue
            self.__data_dict__[k] = v
        return self.__data_dict__

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
        return json.dumps(self._clean_data(), default=self._json_serial, indent=indent)

    def to_dict(self, recursive: bool = True, dates_to_str: bool = False):
        """
        Export stored data as a python dictionary object.
        :param recursive: Boolean, recursively convert nested JSONObjects to a dict
        :param dates_to_str: Boolean, convert all date or datetime values to string.
        """
        data = dict()
        for k, v in self._clean_data().items():
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
