# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The main ConfigHelper class
# ---------------------------------------------------------
# ./ConfigHelper/config_exceptions.py

"""
=======================
Module configExceptions
=======================

Module that define different specific exceptions that can be raised when reading a configuration.
"""

class ConfigSafeMode_NewSection(Exception):
    """ Error raised when an new section is encountered while reading a new configuration. """

class ConfigSafeMode_NewVariable(Exception):
    """ Error raised when an new variable is encountered while reading a new configuration. """

class ConfigRead_fileToBig(Exception):
    """ Error raised before trying to read a file when it exceed the maximum size allowed. """


class ConfigConversionError(Exception):
    """ Error raised when the conversion of a value of the configuration faile.  """