# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Tests for config section
# ---------------------------------------------------------
# tests/test_ConfigHelper/test_configVariable.py
""" Tests for the config_variable module """

import unittest
from py_utils.ConfigHelper.config_section import ConfigSection, _checkNewSection
from py_utils.ConfigHelper.config_variable import ConfigVariable, ConfigConversionError


class TestConfigSection(unittest.TestCase):

    def setUp(self):
        self.var1 = ConfigVariable("var1", str,  "value1")
        self.var2 = ConfigVariable("var2", int,  42)
        self.var3 = ConfigVariable("var3", bool, False)

        self.section = ConfigSection("test_section")
        self.section.add_variable(self.var1)
        self.section.add_variable(self.var2)

    def test_len(self):
        self.assertEqual(len(self.section), 2)

    def test_getattr_and_setattr(self):
        # Accès attribut
        self.assertEqual(self.section.var1, "value1")

        # Modification attribut
        with self.assertRaises(ConfigConversionError):
            self.section.var2 = "new_value"
        
        self.section.var1 = "new_value"
        self.assertEqual(self.section.var1, "new_value")

    def test_getitem_and_setitem(self):
        # Accès indexé
        self.assertEqual(self.section["var2"], 42)

        # Modification indexée
        self.section["var2"] = 100
        self.assertEqual(self.section["var2"], 100)

        # Erreurs de type et KeyError
        with self.assertRaises(TypeError):
            _ = self.section[123]  # Mauvais type
        with self.assertRaises(KeyError):
            _ = self.section["varX"]

    def test_contains(self):
        self.assertIn("var1", self.section)
        self.assertNotIn("var3", self.section)
        self.assertIn(self.var1, self.section)

    def test_add_variable_errors(self):
        # Ajout de variable existante
        with self.assertRaises(KeyError):
            self.section.add_variable(ConfigVariable("var1", str, "dummy"))
        
        # Mauvais type
        with self.assertRaises(TypeError):
            self.section.add_variable(123)

    def test_set_variable(self):
        # Peut remplacer ou ajouter une variable existante
        new_var = ConfigVariable("var1", str, "override")
        self.section.set_variable(new_var)
        self.assertEqual(self.section["var1"], "override")

        # Peut aussi ajouter une nouvelle variable
        self.section.set_variable(self.var3)
        self.assertFalse(self.section["var3"])

    def test_del_variable(self):
        self.section.del_variable("var1")
        self.assertNotIn("var1", self.section)
        
        # Supprimer une variable inexistante ne lève pas d’erreur
        self.section.del_variable("not_existing")

    def test_update_variable(self):
        # Ajoute la variable var1 si elle existe
        updated_var = ConfigVariable("var1", str, "updated")
        self.section.update_variable(updated_var)
        self.assertEqual(self.section["var1"], "updated")

        # Test d’erreur si la variable n’existe pas
        with self.assertRaises(KeyError):
            self.section.update_variable(ConfigVariable("unknown", str, "X"))

        # Mauvais type
        with self.assertRaises(TypeError):
            self.section.update_variable("invalid")

        # Mauvais type de variable
        with self.assertRaises(ConfigConversionError):
            bad_type = ConfigVariable("var2",str,"not convertible to int")
            self.section.update_variable(bad_type)

    def test_with_defaults(self):
        default_section = ConfigSection("test_section")
        default_section.add_variable( ConfigVariable("var2", int, 999) )
        default_section.add_variable( ConfigVariable("var3",bool,True) )
        
        # Ajoute la section par défaut
        new_section = self.section.with_defaults(default_section)

        # Les variables de base sont préservées
        self.assertEqual(new_section["var1"], "value1")
        self.assertEqual(new_section["var2"], 42)

        # La variable par défaut a été ajoutée
        self.assertTrue(new_section["var3"])

        # Les modifications n’affectent pas la section originale
        self.assertNotIn("var3", self.section)

        # TypeError si mauvais type
        with self.assertRaises(TypeError):
            self.section.with_defaults("not_a_section")

    def test_get(self):

        # get() normal
        self.assertEqual(self.section.get("var1"), "value1")

        # get() avec fallback
        self.assertEqual(self.section.get("unknown", fallback="fallback"), "fallback")

        # get() sans fallback (erreur)
        with self.assertRaises(KeyError):
            self.section.get("unknown")

        # get() mauvais type
        with self.assertRaises(TypeError):
            self.section.get(123)

    def test_checkNewSection(self):
        self.assertEqual(_checkNewSection("[section_name]"), "section_name")
        self.assertIsNone(_checkNewSection("not_a_section"))
        with self.assertRaises(TypeError):
            _checkNewSection(123)

    def test_equality(self):
        var1 = ConfigVariable("name",str,"value")
        var2 = ConfigVariable("other_name",str,'value')

        section1 = ConfigSection("section")
        section1.add_variable(var1)
        section1.add_variable(var2)

        section2 = ConfigSection("section")
        section2.add_variable(var1)
        section2.add_variable(var2)

        section3 = ConfigSection("section3")
        section3.add_variable(var1)
        
        self.assertTrue(section1 == section2)
        self.assertFalse(section1 == section3)
