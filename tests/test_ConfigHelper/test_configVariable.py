# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Tests for config variables
# ---------------------------------------------------------
# ./tests/test_ConfigHelper/test_configVariable.py
""" Tests for the config_variable module """

import unittest

from ConfigHelper.config_variable import *
from ConfigHelper.config_variable import \
    _extractFromString

class test_ConfigVariable(unittest.TestCase):
    """ Tests for the ConfigVariable class. """
    def _getConf(self):
        class ConfigMockup():
            varSTR = ConfigVariable.constructFromString('varSTR:str = 2.5')
            varINT = ConfigVariable.constructFromString('varINT:int = 5')
            varFLOAT = ConfigVariable.constructFromString('varFLOAT:float = 2.5')
        return ConfigMockup()
    
    def test_initial_value(self):

        conf = self._getConf()

        self.assertEqual(conf.varSTR,"2.5","Initial value incorrect for class str.")
        self.assertEqual(conf.varINT,5,"Initial value incorrect for class int.")
        self.assertEqual(conf.varFLOAT,2.5,"Initial value incorrect for class float.")
    def test_initial_type(self):
        
        conf = self._getConf()

        self.assertIsInstance(conf.varSTR,str,"Initial type incorrect for class str.")
        self.assertIsInstance(conf.varINT,int,"Initial type incorrect for class int.")
        self.assertIsInstance(conf.varFLOAT,float,"Initial type incorrect for class float.")
    def test_bad_newValue(self):

        conf = self._getConf()

        with self.assertRaises(TypeError):
            conf.varINT = 'test'
            conf.varFLOAT = 'test'
    def test_good_newValue_type(self):
        
        conf = self._getConf()

        # Without conversion:
        conf.varSTR = "test"
        conf.varINT = 2
        conf.varFLOAT = 0.5

        self.assertIsInstance(conf.varSTR,str,"New value type without conversion incorrect for class str.")
        self.assertIsInstance(conf.varINT,int,"New value type without conversion incorrect for class int.")
        self.assertIsInstance(conf.varFLOAT,float,"New value type without conversion incorrect for class float.")

        # With conversion:
        conf.varINT = "5"
        conf.varFLOAT = "2.5"

        self.assertIsInstance(conf.varINT,int,"New value type with conversion incorrect for class int.")
        self.assertIsInstance(conf.varFLOAT,float,"New value type with conversion incorrect for class float.")
    def test_good_newValue_value(self):

        conf = self._getConf()

        # Without conversion:
        conf.varSTR = "test"
        conf.varINT = 2
        conf.varFLOAT = 0.5

        self.assertEqual(conf.varSTR,"test","New value value without conversion incorrect for class str.")
        self.assertEqual(conf.varINT,2,"New value value without conversion incorrect for class int.")
        self.assertEqual(conf.varFLOAT,0.5,"New value value without conversion incorrect for class float.")

        # With conversion:
        conf.varINT = "5"
        conf.varFLOAT = "2.5"

        self.assertEqual(conf.varINT,5,"New value value with conversion incorrect for class int.")
        self.assertEqual(conf.varFLOAT,2.5,"New value value with conversion incorrect for class float.")

class test_extraction(unittest.TestCase):
    """ Tests for the differents extraction functions.

    This TestCase test the following extraction function:
    - _extractFromString

    The ability of each function to extract correctly all the required 
    informations are tested.
    """

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

