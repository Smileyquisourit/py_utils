# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Initialisation of Logueur
# ---------------------------------------------------------
# py_utils/ConfigHelper/__init__.py

"""
    ============
    ConfigHelper
    ============

    This module provides a interface for differents configuration files. The supported
    format of the configuration file are INI and JSON.

    Objects
    -------

    ConfigHelper:
        The main interface to a configuration. It can read differents configuration files
        of different format.

    ConfigSection:
        Represent a section of a configuration.

    ConfigVariable:
        Represent one variable of a configuration, and contain it's name, type and value.
"""

# Expose main interfaces:
# -----------------------

from .confighelper import ConfigHelper
from .config_section import ConfigSection
from .config_variable import ConfigVariable


# TODO list:
# ----------
# - Add UNSAFE exception when creating a config
# - __repr__ of ConfigVariable print <class str> (or int, float)
# - Add _doc or doc in ConfigVariable to explain a variable in the config (will be print as comment when
#   writting a config file)
# - See TODO in function _extract_from_dict of module config_variable
# - See notes of read method of ConfigHelper. The behavior should be changed in the same time we implement
#   the interpolation because both need to first parse the configuration, then add the variable.
# - Add interpolation for INI format configuration (and JSON), with %{SECTION:NAME}s or %{NAME}s
# - Add verification logic for the name of a ConfigVariable and of a ConfigSection
# - For preventing too much memory usage, add or modify the logic to check for the size in byte and not 
# (only) for the number of line.
# - Return a tuple or iterator when calling XX.items() and not a dictionary view (there shouldn't be something that 
#   enable the user to change the value, and this may be the case when returning dict.items())
# - Add equality operator for config section and variable
# - Check thaht the ConfigSection with_defaults() is used when it should be (ie in getitem, getattribute, get, ...)
# - Add generic type for the config classes, see https://docs.python.org/3/library/stdtypes.html#types-genericalias
# - see https://en.wikipedia.org/wiki/INI_file for more idea