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
#       writting a config file) 
# - Change _NO_FALLBACK to a more elegant solution if possible, else see where to define it
# - Implement read and read_safe
#
# - Add supported type: bool (with 'on'/'off', 'True'/'False', 'true'/'false', 'yes'/'no')
# - Add interpolation for INI format configuration, with %{SECTION:NAME}s or %{NAME}s
# - Add verification logic for the name of a ConfigVariable and of a ConfigSection
#
# - Add generic type for the config classes, see https://docs.python.org/3/library/stdtypes.html#types-genericalias
# - see https://en.wikipedia.org/wiki/INI_file for more idea