# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Tests for config helper
# ---------------------------------------------------------
# tests/test_ConfigHelper/test_configHelper.py
""" Tests for the confighelper module """

import unittest
import tempfile
import unittest.mock

from py_utils.ConfigHelper.confighelper import *

class TestConfigHelper(unittest.TestCase):

    def setUp(self):
        """Set up a fresh ConfigHelper instance before each test."""
        self.conf = ConfigHelper()

    def test_add_and_get_section(self):
        """Test adding and retrieving a section."""
        section = ConfigSection("my_section")
        self.conf.add_section(section)
        self.assertIn("my_section", self.conf.sections_names)
        self.assertIsInstance(self.conf["my_section"], ConfigSection)
        self.assertIsInstance(self.conf.my_section, ConfigSection)

    def test_add_duplicate_section_raises(self):
        """Adding a duplicate section raises KeyError."""
        section = ConfigSection("duplicate")
        self.conf.add_section(section)
        with self.assertRaises(KeyError):
            self.conf.add_section(section)

    def test_set_section_overwrites(self):
        """set_section should overwrite an existing section."""
        section1 = ConfigSection("overwrite")
        section2 = ConfigSection("overwrite")
        section2.add_variable(ConfigVariable('var',str,'test'))
        self.conf.set_section(section1)
        self.conf.set_section(section2)
        self.assertEqual(self.conf["overwrite"]._name, section2._name)
        self.assertEqual(self.conf["overwrite"]._vars, section2._vars)
        # Fail but shouldn't: self.asssertIs(self.conf['overwrite'], section2)
        # Maybe a copy is made ?

    def test_del_section(self):
        """Test deleting a section."""
        section = ConfigSection("to_delete")
        self.conf.add_section(section)
        self.conf.del_section("to_delete")
        self.assertNotIn("to_delete", self.conf.sections_names)
    
    def test_update_section_creates_section(self):
        """update_section should create section if it doesn't exist."""
        var = ConfigVariable("my_var", str,"value")
        self.conf.update_section("new_section", var)
        self.assertIn("new_section", self.conf.sections_names)
        self.assertEqual(self.conf["new_section"].get("my_var"), var.value)

    def test_set_default_variable(self):
        """set_default should add variable to defaults."""
        var = ConfigVariable("default_var", str, "val")
        self.conf.set_default(var)
        self.assertIn("default_var", self.conf.defaults_names)
    
    def test_get_variable_from_defaults(self):
        """Test getting a variable from defaults when section does not exist."""
        var = ConfigVariable("var1", str, "val1")
        self.conf.set_default(var)
        self.assertEqual(self.conf.get(None, "var1"), var.value)

    def test_len_counts_all_vars(self):
        """Test __len__ correctly counts all variables."""
        var1 = ConfigVariable("v1", int, "1")
        var2 = ConfigVariable("v2", int, "2")
        section = ConfigSection("sec")
        section.set_variable(var2)
        self.conf.set_default(var1)
        self.conf.set_section(section)
        self.assertEqual(len(self.conf), 2)

    def test_contains(self):
        """Test __contains__ method."""
        var = ConfigVariable("var", str, "value")
        self.conf.set_default(var)
        self.assertIn("var", self.conf)
        self.assertNotIn("missing", self.conf)

    def test_getitem_and_errors(self):
        """Test __getitem__ and error handling."""
        var = ConfigVariable("v", int, "1")
        self.conf.set_default(var)
        section = ConfigSection("s")
        self.conf.set_section(section)
        with self.assertRaises(KeyError):
            _ = self.conf["missing_section"]

        self.assertEqual(self.conf["s"]._name, "s")
        with self.assertRaises(TypeError):
            _ = self.conf[123]

    def test_setitem_raises(self):
        """__setitem__ should raise error."""
        with self.assertRaises(AttributeError):
            self.conf["any"] = "value"

    def test_comment_indicators_customization(self):
        """Test that custom comment indicators can be set."""
        custom_conf = ConfigHelper(comments_indicators="!")
        conf_str = "! a comment\nvar=value"
        self.assertEqual(custom_conf._comments_indicators, "!")
        custom_conf.read_str(conf_str)
        self.assertEqual(len(custom_conf), 1)

    def test_new_creates_fresh_defaults_and_sections(self):
        """Test __new__ creates new empty sections and defaults."""
        c = ConfigHelper()
        self.assertIsInstance(c._DEFAULTS, ConfigSection)
        self.assertEqual(len(c._SECTIONS), 0)

    def test_add_section_success(self):
        section = ConfigSection('section1')
        self.conf.add_section(section)
        self.assertIn('section1', self.conf._SECTIONS)

        # Duplicate
        with self.assertRaises(KeyError):
            self.conf.add_section(section)

        # Wrong type
        with self.assertRaises(TypeError):
            self.conf.add_section("not_a_section")

    def test_set_section_success(self):

        section = ConfigSection('section1')
        self.conf.set_section(section)
        self.assertIn('section1', self.conf._SECTIONS)

        # Wrong type
        with self.assertRaises(TypeError):
            self.conf.set_section("not_a_section")

    def test_del_section(self):
        section = ConfigSection('section1')
        self.conf.add_section(section)
        self.conf.del_section('section1')
        self.assertNotIn('section1', self.conf._SECTIONS)

        # Not existing:
        self.conf.del_section('nonexistent')  # Should do nothing
        self.assertNotIn('nonexistent', self.conf._SECTIONS)

    def test_update_section(self):
        var = ConfigVariable('var1', str, 'value1')
        self.conf.update_section('section1', var)
        self.assertIn('section1', self.conf._SECTIONS)
        self.assertIn('var1', self.conf._SECTIONS['section1'].keys())

        # default
        var = ConfigVariable('var2', str, 'value2')
        self.conf.update_section(None, var)
        self.assertIn('var2', self.conf._DEFAULTS.keys())

        # Wrong type
        with self.assertRaises(TypeError):
            self.conf.update_section(123, ConfigVariable('var1', 'value1'))
        with self.assertRaises(TypeError):
            self.conf.update_section('section', 'not_a_var')

    def test_set_default(self):

        var = ConfigVariable('var1', str, 'value1')
        self.conf.set_default(var)
        self.assertIn('var1', self.conf._DEFAULTS.keys())

        # Wrong type
        with self.assertRaises(TypeError):
            self.conf.set_default("not_a_var")


    def test_read_str_basic(self):
        conf_str = """
var1 = val1
[section1]
var2 = val2
"""
        self.conf.read_str(conf_str)
        self.assertIn('section1', self.conf._SECTIONS)
        self.assertIn('var1', self.conf._DEFAULTS.keys())
        self.assertIn('var2', self.conf._SECTIONS['section1'].keys())

        #
    def test_read_dict_basic(self):
        conf_dict = {
            "DEFAULTS": [{"name":"var1", "value":"val1"}],
            "SECTIONS": [
                {"section1": [{"name":"var2", "value":"val2"}]}
            ]
        }
        self.conf.read_dict(conf_dict)
        self.assertIn('var1', self.conf._DEFAULTS.keys())
        self.assertIn('section1', self.conf._SECTIONS)
        self.assertIn('var2', self.conf._SECTIONS['section1'].keys())

    def test_read_dict_arg_error(self):

        # Wrong type
        with self.assertRaises(TypeError):
            self.conf.read_dict("not_a_dict")

        #
    def test_read_dict_incorrect_fmt(self):

        # No sections
        conf_dict = {"DEFAULTS": [{"name":"var1", "value":"val1"}]}
        with self.assertRaises(ValueError):
            self.conf.read_dict(conf_dict)

        # Wrong type for section
        conf_dict = {
            "DEFAULTS": [{"name":"var1", "value":"val1"}],
            "SECTIONS": "not_a_list"
        }
        with self.assertRaises(TypeError):
            self.conf.read_dict(conf_dict)

        # Wrong fmt for variables
        conf_dict = {
            "DEFAULTS": [{"name":"var1", "value":"val1"}],
            "SECTIONS": [{"section1": [{"name":"var2", "value":"val2"}], "extra": "oops"}]
        }
        with self.assertRaises(ValueError):
            self.conf.read_dict(conf_dict)

    def test_read_json_success(self):
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            json.dump({
                "DEFAULTS": [{"name":"var1", "value":"val1"}],
                "SECTIONS": [{"section1": [{"name":"var2", "value":"val2"}]}]
            }, f)
            f.flush()
            
            self.conf.read_json(f.name)
            self.assertIn('var1', self.conf._DEFAULTS.keys())

    def test_read_json_error(self):
        with self.assertRaises(FileNotFoundError):
            self.conf.read_json('nonexistent.json')

        with tempfile.NamedTemporaryFile('w+') as f:
            json.dump({
                "DEFAULTS": [{"name":"var1", "value":"val1"}],
                "SECTIONS": [{"section1": [{"name":"var2", "value":"val2"}]}]
            }, f)
            f.flush()

            new_conf = ConfigHelper(file_maxSize=10)
            with self.assertRaises(ConfigRead_fileToBig):
                new_conf.read_json(f.name)
    
    def test_read_json_ignoreSize(self):

        with tempfile.NamedTemporaryFile('w+') as f:
            json.dump({
                "DEFAULTS": [{"name":"var1", "value":"val1"}],
                "SECTIONS": [{"section1": [{"name":"var2", "value":"val2"}]}]
            }, f)
            f.flush()

            with unittest.mock.patch('py_utils.ConfigHelper.confighelper._DEFAULT_MAX_SIZE',10):
                new_conf = ConfigHelper(file_maxSize=-1)
                try:
                    new_conf.read_json(f.name)
                except ConfigRead_fileToBig as e:
                    self.fail("Exception file too big raised when max size < 0")

    def test_read_ini_success(self):
        ini_content = """
var1 = val1
[section1]
var2 = val2
"""
        with tempfile.NamedTemporaryFile('w+') as f:
            f.write(ini_content)
            f.flush()

            self.conf.read_ini(f.name)
            self.assertIn('section1', self.conf._SECTIONS)
            self.assertIn('var1', self.conf._DEFAULTS.keys())

    def test_read_ini_errors(self):

        # File not found
        with self.assertRaises(FileNotFoundError):
            self.conf.read_ini('nonexistent.ini')

        # File to big
        with tempfile.NamedTemporaryFile('w+') as f:
            for _ in range(110):
                f.write("var = val\n")
            f.flush()

            new_conf = ConfigHelper(file_maxSize=10)
            with self.assertRaises(ConfigRead_fileToBig):
                new_conf.read_ini(f.name)

        # Too many lines
        with tempfile.NamedTemporaryFile('w+') as f:
            for _ in range(110):
                f.write("var = val\n")
                f.flush()

            with self.assertRaises(Exception):
                self.conf.read_ini(f.name, max_lines=100)
    
    def test_read_ini_ignoreSize(self):

        with tempfile.NamedTemporaryFile('w+') as f:
            for _ in range(50):
                f.write("var = val\n")
            f.flush()

            with unittest.mock.patch('py_utils.ConfigHelper.confighelper._DEFAULT_MAX_SIZE',10):
                new_conf = ConfigHelper(file_maxSize=-1)
                try:
                    new_conf.read_ini(f.name)
                except ConfigRead_fileToBig as e:
                    self.fail("Exception file too big raised when max size < 0")


    def test_read_correctObject(self):
        
        # String
        with unittest.mock.patch.object(self.conf,'read_str') as patch:
            self.conf._read("some str that shouldn't be a file",False,False)
        patch.assert_called()
        
        # Dict
        with unittest.mock.patch.object(self.conf,'read_dict') as patch:
            self.conf._read({'dict':'configuration'},False,False)
        patch.assert_called()
        
        # JSON
        with unittest.mock.patch.object(self.conf,'read_json') as patch:
            with tempfile.NamedTemporaryFile('r',suffix='.json') as f:
                self.conf._read(f.name,False,False)
        patch.assert_called()

        # INI
        with unittest.mock.patch.object(self.conf,'read_ini') as patch:
            with tempfile.NamedTemporaryFile('r') as f:
                self.conf._read(f.name,False,False)
        patch.assert_called()
        #
    def test_read_returnValue(self):

        # Correct config:
        test = self.conf._read("varName : str = varValue",False,False)
        self.assertTrue(test)

        # Uncorrect config (type that don't exist):
        test = self.conf._read("varName : varType = varValue",False,False)
        self.assertFalse(test)
        #
    def test_read_argsError(self):
        with self.assertRaises(TypeError):
            self.conf._read(42,False,False)
        with self.assertRaises(TypeError):
            self.conf._read("a str",safe=5,warn=False)
        with self.assertRaises(TypeError):
            self.conf._read("a str",safe=False,warn=5)
