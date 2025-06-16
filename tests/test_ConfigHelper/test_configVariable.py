# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Tests for config variables
# ---------------------------------------------------------
# tests/test_ConfigHelper/test_configVariable.py
""" Tests for the config_variable module """

import unittest

from py_utils.ConfigHelper.config_variable import *
from py_utils.ConfigHelper.config_variable import \
    _extractFromString, \
    _extractFromDict, \
    _SUPPORTED_TYPE, _CONVERSION_FUNC

class new_type():
    pass

class test_ConfigVariable(unittest.TestCase):
    """ Tests for the ConfigVariable class. """
    def test_valid_initialization(self):
        var = ConfigVariable("test_var", int, "123")
        self.assertEqual(var.value, 123)
        self.assertEqual(var.type, int)

    def test_type_immutable(self):
        var = ConfigVariable("test_var", int, 10)
        with self.assertRaises(AttributeError):
            var.type = str

    def test_invalid_type_string(self):
        with self.assertRaises(ValueError):
            ConfigVariable("test_var", "unknown", 10)

    def test_invalid_type_object(self):
        with self.assertRaises(ValueError):
            ConfigVariable("test_var", list, [])

    def test_equality(self):
        var1 = ConfigVariable("name",str,"value")
        var2 = ConfigVariable("name",str,"value")
        self.assertTrue(var1 == var2)

        var3 = ConfigVariable("other_name",str,'value')
        self.assertFalse(var1 == var3)

    def test_value_setter_converts(self):
        var = ConfigVariable("v", int, "42")
        var.value = "100"
        self.assertEqual(var.value, 100)

    def test_register_decorator(self):
        
        @ConfigVariable.register(new_type)
        def to_bool(val):
            return str(val).lower() in ["1", "true", "yes"]

        self.assertIn("new_type", _SUPPORTED_TYPE.keys())
        self.assertIn(to_bool, _CONVERSION_FUNC.values())
        self.assertTrue(_CONVERSION_FUNC[new_type]("true", "flag", bool))


class test_STR_extraction(unittest.TestCase):

    # _extractFromString:
    # -------------------
    def test_escapeWhiteSpaceWhithoutType(self):
        lines = (
            "name=value",
            "name =value",
            "name= value",
            "name = value",
            "name    =     value"
        )

        for line in lines:
            rslt = _extractFromString(line)
            self.assertEqual("OK",rslt[1],f"'{line}' uncorrectly extracted!!")
    def test_escapeWhiteSpaceWhithType(self):
        lines = (
            "name:int    = value",
            "name :float = value",
            "name: str   = value",
            "name : int = value",
            "name:int = value"
        )
        for line in lines:
            rslt = _extractFromString(line)
            self.assertEqual("OK",rslt[1],f"'{line}' uncorrectly extracted!!")
    def test_uncorrectString(self):
        lines = (
            "name",
            "=value",
            ":int = value",
            "name : value"
        )
        err_codes = (
            "NO_VALUE_FOUND",
            "NO_NAME_FOUND",
            "NO_NAME_FOUND",
            "UNSUPORTED_TYPE"
        )
        for line,err_code in zip(lines,err_codes):
            rslt = _extractFromString(line)
            self.assertEqual(err_code,rslt[1])


class test_DICT_extraction(unittest.TestCase):

    def test_valid_input(self):
        data = {"name": "age", "type": "int", "value": 30}
        expected = (
            {"name": "age", "type": int, "value": 30},
            "OK",
            ""
        )
        self.assertEqual(_extractFromDict(data), expected)

    def test_missing_name(self):
        data = {"type": "int", "value": 42}
        result = _extractFromDict(data)
        self.assertEqual(result[1], "NO_NAME_FOUND")
        self.assertEqual(result[2], "No name found in dict!")

    def test_unsupported_type(self):
        data = {"name": "temperature", "type": "complex", "value": 42}
        result = _extractFromDict(data)
        self.assertEqual(result[1], "UNSUPORTED_TYPE")
        self.assertIn("Unsuported type complex", result[2])

    def test_non_str_type(self):
        class Custom:
            pass
        data = {"name": "field", "type": Custom, "value": "x"}
        result = _extractFromDict(data)
        self.assertEqual(result[1], "UNSUPORTED_TYPE")
        self.assertIn("Unsuported type Custom", result[2])

    def test_missing_value(self):
        data = {"name": "username", "type": "str"}
        result = _extractFromDict(data)
        self.assertEqual(result[1], "NO_VALUE_FOUND")
        self.assertEqual(result[2], "No value found in dict!")

    def test_default_type(self):
        data = {"name": "username", "value": "admin"}
        expected = (
            {"name": "username", "type": str, "value": "admin"},
            "OK",
            ""
        )
        self.assertEqual(_extractFromDict(data), expected)
