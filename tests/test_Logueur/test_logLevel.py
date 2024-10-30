# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Test for the different log levels
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logLevel.py
""" Tests for the log_level module """

import unittest

from Logueur.log_level import *

class test_LogLevel(unittest.TestCase):
    """ Tests for the LogLevel class 
    
    We test each operator and the factory function.
    For each operator, we always have 3 case:
    - when b is strictly inferior to a
    - when b is equal to a
    - when b is strictly inferior to a
    """
    
    # b < a
    def test_lowerThan(self):
        b = LogLevel(1)
        b_int = 1
        b_str = "INFO"
        a1 = LogLevel(2)
        a2 = LogLevel(1)
        a3 = LogLevel(0)

        # Strictly inferior
        self.assertTrue(b < a1, msg="Error asserting lower than using LogLevel (strictly inferior)")
        self.assertTrue(b_int < a1, msg= "Error asserting lower than using int (strictly inferior)")
        self.assertTrue(b_str < a1, msg= "Error asserting lower than using str (strictly inferior)")

        # Equal
        self.assertFalse(b < a2, msg="Error asserting lower than using LogLevel (equal)")
        self.assertFalse(b_int < a2, msg= "Error asserting lower than using int (equal)")
        self.assertFalse(b_str < a2, msg= "Error asserting lower than using str (equal)")

        # Strictly superior
        self.assertFalse(b < a3, msg="Error asserting lower than using LogLevel (strictly superior)")
        self.assertFalse(b_int < a3, msg= "Error asserting lower than using int (strictly superior)")
        self.assertFalse(b_str < a3, msg= "Error asserting lower than using str (strictly superior)")

    # b <= a
    def test_lowerOrEqual(self):
        b = LogLevel(1)
        b_int = 1
        b_str = "INFO"
        a1 = LogLevel(2)
        a2 = LogLevel(1)
        a3 = LogLevel(0)

        # Strictly inferior
        self.assertTrue(b <= a1, msg="Error asserting lower or equal using LogLevel (strictly inferior)")
        self.assertTrue(b_int <= a1, msg= "Error asserting lower or equal using int (strictly inferior)")
        self.assertTrue(b_str <= a1, msg= "Error asserting lower or equal using str (strictly inferior)")

        # Equal
        self.assertTrue(b <= a2, msg="Error asserting lower or equal using LogLevel (equal)")
        self.assertTrue(b_int <= a2, msg= "Error asserting lower or equal using int (equal)")
        self.assertTrue(b_str <= a2, msg= "Error asserting lower or equal using str (equal)")

        # Strictly superior
        self.assertFalse(b <= a3, msg="Error asserting lower or equal using LogLevel (strictly superior)")
        self.assertFalse(b_int <= a3, msg= "Error asserting lower or equal using int (strictly superior)")
        self.assertFalse(b_str <= a3, msg= "Error asserting lower or equal using str (strictly superior)")
    
    # b == a
    def test_equal(self):
        b = LogLevel(1)
        b_int = 1
        b_str = "INFO"
        a1 = LogLevel(2)
        a2 = LogLevel(1)
        a3 = LogLevel(0)

        # Strictly inferior
        self.assertFalse(b == a1, msg="Error asserting equal using LogLevel (strictly inferior)")
        self.assertFalse(b_int == a1, msg= "Error asserting equal using int (strictly inferior)")
        self.assertFalse(b_str == a1, msg= "Error asserting equal using str (strictly inferior)")

        # Equal
        self.assertTrue(b == a2, msg="Error asserting equal using LogLevel (equal)")
        self.assertTrue(b_int == a2, msg= "Error asserting equal using int (equal)")
        self.assertTrue(b_str == a2, msg= "Error asserting equal using str (equal)")

        # Strictly superior
        self.assertFalse(b == a3, msg="Error asserting equal using LogLevel (strictly superior)")
        self.assertFalse(b_int == a3, msg= "Error asserting equal using int (strictly superior)")
        self.assertFalse(b_str == a3, msg= "Error asserting equal using str (strictly superior)")
    
    # b != a
    def test_notEqual(self):
        b = LogLevel(1)
        b_int = 1
        b_str = "INFO"
        a1 = LogLevel(2)
        a2 = LogLevel(1)
        a3 = LogLevel(0)

        # Strictly inferior
        self.assertTrue(b != a1, msg="Error asserting equal using LogLevel (strictly inferior)")
        self.assertTrue(b_int != a1, msg= "Error asserting equal using int (strictly inferior)")
        self.assertTrue(b_str != a1, msg= "Error asserting equal using str (strictly inferior)")

        # Equal
        self.assertFalse(b != a2, msg="Error asserting equal using LogLevel (equal)")
        self.assertFalse(b_int != a2, msg= "Error asserting equal using int (equal)")
        self.assertFalse(b_str != a2, msg= "Error asserting equal using str (equal)")

        # Strictly superior
        self.assertTrue(b != a3, msg="Error asserting equal using LogLevel (strictly superior)")
        self.assertTrue(b_int != a3, msg= "Error asserting equal using int (strictly superior)")
        self.assertTrue(b_str != a3, msg= "Error asserting equal using str (strictly superior)")

    # b > a
    def test_greaterThan(self):
        b = LogLevel(1)
        b_int = 1
        b_str = "INFO"
        a1 = LogLevel(2)
        a2 = LogLevel(1)
        a3 = LogLevel(0)

        # Strictly inferior
        self.assertFalse(b > a1, msg="Error asserting greater using LogLevel (strictly inferior)")
        self.assertFalse(b_int > a1, msg= "Error asserting greater using int (strictly inferior)")
        self.assertFalse(b_str > a1, msg= "Error asserting greater using str (strictly inferior)")

        # Equal
        self.assertFalse(b > a2, msg="Error asserting greater using LogLevel (equal)")
        self.assertFalse(b_int > a2, msg= "Error asserting greater using int (equal)")
        self.assertFalse(b_str > a2, msg= "Error asserting greater using str (equal)")

        # Strictly superior
        self.assertTrue(b > a3, msg="Error asserting greater using LogLevel (strictly superior)")
        self.assertTrue(b_int > a3, msg= "Error asserting greater using int (strictly superior)")
        self.assertTrue(b_str > a3, msg= "Error asserting greater using str (strictly superior)")
    
    # b >= a
    def test_greaterOrEqual(self):
        b = LogLevel(1)
        b_int = 1
        b_str = "INFO"
        a1 = LogLevel(2)
        a2 = LogLevel(1)
        a3 = LogLevel(0)

        # Strictly inferior
        self.assertFalse(b >= a1, msg="Error asserting greater or equal using LogLevel (strictly inferior)")
        self.assertFalse(b_int >= a1, msg= "Error asserting greater or equal using int (strictly inferior)")
        self.assertFalse(b_str >= a1, msg= "Error asserting greater or equal using str (strictly inferior)")

        # Equal
        self.assertTrue(b >= a2, msg="Error asserting greater or equal using LogLevel (equal)")
        self.assertTrue(b_int >= a2, msg= "Error asserting greater or equal using int (equal)")
        self.assertTrue(b_str >= a2, msg= "Error asserting greater or equal using str (equal)")

        # Strictly superior
        self.assertTrue(b >= a3, msg="Error asserting greater or equal using LogLevel (strictly superior)")
        self.assertTrue(b_int >= a3, msg= "Error asserting greater or equal using int (strictly superior)")
        self.assertTrue(b_str >= a3, msg= "Error asserting greater or equal using str (strictly superior)")


    # factory
    def test_factory_DEBUG(self):
        test_int = LogLevel.factory(0)
        test_str = LogLevel.factory("DEBUG")

        self.assertTrue(isinstance(test_int,LogLevel))
        self.assertTrue(isinstance(test_str,LogLevel))

        self.assertEqual(0,test_int.value)
        self.assertEqual(0,test_str.value)

        self.assertEqual("DEBUG",test_int.name)
        self.assertEqual("DEBUG",test_str.name)
    def test_factory_INFO(self):
        test_int = LogLevel.factory(1)
        test_str = LogLevel.factory("INFO")

        self.assertTrue(isinstance(test_int,LogLevel))
        self.assertTrue(isinstance(test_str,LogLevel))

        self.assertEqual(1,test_int.value)
        self.assertEqual(1,test_str.value)

        self.assertEqual("INFO",test_int.name)
        self.assertEqual("INFO",test_str.name)
    def test_factory_WARNING(self):
        test_int = LogLevel.factory(2)
        test_str = LogLevel.factory("WARNING")

        self.assertTrue(isinstance(test_int,LogLevel))
        self.assertTrue(isinstance(test_str,LogLevel))

        self.assertEqual(2,test_int.value)
        self.assertEqual(2,test_str.value)

        self.assertEqual("WARNING",test_int.name)
        self.assertEqual("WARNING",test_str.name)
    def test_factory_ERROR(self):
        test_int = LogLevel.factory(3)
        test_str = LogLevel.factory("ERROR")

        self.assertTrue(isinstance(test_int,LogLevel))
        self.assertTrue(isinstance(test_str,LogLevel))

        self.assertEqual(3,test_int.value)
        self.assertEqual(3,test_str.value)

        self.assertEqual("ERROR",test_int.name)
        self.assertEqual("ERROR",test_str.name)
    def test_factory_FATAL(self):
        test_int = LogLevel.factory(4)
        test_str = LogLevel.factory("FATAL")

        self.assertTrue(isinstance(test_int,LogLevel))
        self.assertTrue(isinstance(test_str,LogLevel))

        self.assertEqual(4,test_int.value)
        self.assertEqual(4,test_str.value)

        self.assertEqual("FATAL",test_int.name)
        self.assertEqual("FATAL",test_str.name)
