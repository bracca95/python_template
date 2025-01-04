# inspired by quicktype.io

import os
import sys
import json

from dataclasses import dataclass
from typing import Optional, Union, List, Any, Callable, Iterable, Type, cast

from .tools import Tools, Logger
from ..config.consts import *

def from_bool(x: Any) -> bool:
    Tools.check_instance(x, bool)
    return x

def from_int(x: Any) -> int:
    Tools.check_instance(x, int)
    return x

def from_str(x: Any) -> str:
    Tools.check_instance(x, str)
    return x

def from_none(x: Any) -> Any:
    Tools.check_instance(x, None)
    return x

def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    Tools.check_instance(x, list)
    return [f(y) for y in x]

def from_union(fs: Iterable[Any], x: Any):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    raise TypeError(f"{x} should be one out of {[type(f.__name__) for f in fs]}")


def to_class(c: Type[T], x: Any) -> dict:
    Tools.check_instance(x, c)
    return cast(Any, x).serialize()


@dataclass
class ObjectList:
    obj_id: Optional[int]
    obj_desc: Optional[str]

    @classmethod
    def deserialize(cls, obj: Any) -> 'ObjectList':
        try:
            obj_id = from_union([from_none, from_int], obj.get(CONFIG_OBJECT_OBJ_ID))
            obj_desc = from_union([from_none, from_str], obj.get(CONFIG_OBJECT_OBJ_DESC))
        except ValueError as ve:
            Logger.instance().critical(ve.args)
            sys.exit(-1)

        Logger.instance().info(f"ObjectList:: obj_id: {obj_id}, obj_desc: {obj_desc}")
        return ObjectList(obj_id, obj_desc)

    def serialize(self) -> dict:
        result: dict = {}
        
        result[CONFIG_OBJECT_OBJ_ID] = from_union([from_none, from_int], self.obj_id)
        result[CONFIG_OBJECT_OBJ_DESC] = from_union([from_none, from_str], self.obj_desc)

        Logger.instance().info(f"ObjectList serialized: {result}")
        return result


@dataclass
class Config:
    sample_bool: Optional[bool] = None
    sample_path: Optional[str] = None
    sample_string: Optional[str] = None
    sample_int: Optional[int] = None
    simple_list: Optional[List[str]] = None
    object_list: Optional[List[ObjectList]] = None

    @classmethod
    def deserialize(cls, str_path: str) -> 'Config':
        obj = Tools.read_json(str_path)
        
        try:
            sample_bool_tmp = from_union([from_str, from_bool, from_none], obj.get(CONFIG_SAMPLE_BOOL))
            sample_bool = Tools.str2bool(sample_bool_tmp) if isinstance(sample_bool_tmp, str) else sample_bool_tmp

            sample_path = from_union([from_none, from_str], obj.get(CONFIG_SAMPLE_PATH))
            if sample_path is not None:
                sample_path = Tools.validate_path(sample_path)

            sample_string = from_union([from_none, from_str], obj.get(CONFIG_SAMPLE_STRING))
            sample_int = from_union([from_none, from_int], obj.get(CONFIG_SAMPLE_INT))
            simple_list = from_union([lambda x: from_list(from_str, x), from_none], obj.get(CONFIG_SIMPLE_LIST))
            object_list = from_union([lambda x: from_list(ObjectList.deserialize, x), from_none], obj.get(CONFIG_OBJECT_LIST))
        except TypeError as te:
            Logger.instance().critical(te.args)
            sys.exit(-1)
        except FileNotFoundError as fnf:
            Logger.instance().critical(fnf.args)
            sys.exit(-1)
        
        Logger.instance().info(f"Config deserialized: " +
            f"sample_bool: {sample_bool}, sample_path: {sample_path}, sample_string: {sample_string}, " +
            f"sample_int: {sample_int}, simple_list: {simple_list}, object_list: {object_list}")
        
        return Config(sample_bool, sample_path, sample_string, sample_int, simple_list, object_list)

    def serialize(self, directory: str, filename: str):
        result: dict = {}
        dire = None

        try:
            dire = Tools.validate_path(directory)
        except FileNotFoundError as fnf:
            Logger.instance().critical(f"{fnf.args}")
            sys.exit(-1)
        
        # if you do not want to write null values, add a field to result if and only if self.field is not None
        result[CONFIG_SAMPLE_BOOL] = from_union([from_none, from_bool], self.sample_bool)
        result[CONFIG_SAMPLE_PATH] = from_union([from_none, from_str], self.sample_path)
        result[CONFIG_SAMPLE_STRING] = from_union([from_none, from_str], self.sample_string)
        result[CONFIG_SAMPLE_INT] = from_union([from_none, from_int], self.sample_int)
        result[CONFIG_SIMPLE_LIST] = from_union([lambda x: from_list(from_str, x), from_none], self.simple_list)
        result[CONFIG_OBJECT_LIST] = from_union([lambda x: from_list(lambda y: to_class(ObjectList, y), x), from_none], self.object_list)

        with open(os.path.join(dire, filename), "w") as f:
            json_dict = json.dumps(result, indent=4)
            f.write(json_dict)

        Logger.instance().info("Config serialized")


def config_to_json(x: Config) -> Any:
    return to_class(Config, x)
