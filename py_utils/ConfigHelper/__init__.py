# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Initialisation of Logueur
# ---------------------------------------------------------
# py_utils/ConfigHelper/__init__.py

"""
The :mod:`~py_utils.ConfigHelper.confighelper` module provides a flexible framework for reading and managing
configuration data. It supports loading configurations from:

- Plain text files (using a custom INI-like format)
- JSON files (with a specific structure)
- Python objects (such as :class:`str` or :class:`dict`)

Configurations are structured into three hierarchical levels:

1. The top-level :class:`~py_utils.ConfigHelper.confighelper.ConfigHelper` object, which serves
   as the main interface.
2. One or more :class:`~py_utils.ConfigHelper.config_section.ConfigSection` objects, representing
   configuration sections.
3. Each section contains multiple :class:`~py_utils.ConfigHelper.config_variable.ConfigVariable`
   objects, representing individual typed variables.

The configuration can be accessed using *attribute syntax* (e.g., `conf.section.variable`),
*item syntax* (e.g., `conf['section']['variable']`), or a mix of both. You can also define
default variables, which are accessible by all sections if they don't declare them.

Each variable is defined with a type and a value. Upon creation, the value is automatically
converted to the specified type. Some python types are already supported, but you can register custom 
types by providing your own **conversion functions**.

The supported types are:

- :class:`str`, the default one
- :class:`int`,
- :class:`float`,
- :class:`bool`, from value like `True`, `False`, `on`, `off`, ...

Although configuration values are internally represented as :class:`~py_utils.ConfigHelper.config_variable.ConfigVariable`
instances, accessing them through the configuration object returns the actual value, not the wrapper object.

You can read multiple configurations, the last one read will overwrite the values of preceding ones. This facilitates a 
default configuration that can be overridden by user-provided values, or read potential configuration from different location 
(like the current directory, the user's home directory, and some system-wide directory).
"""

__all__ = ["ConfigHelper", "ConfigSection", "ConfigVariable"]


# Expose main interfaces:
# -----------------------

from .confighelper import ConfigHelper
from .config_section import ConfigSection
from .config_variable import ConfigVariable


# TODO list:
# ----------
# - Add _doc or doc in ConfigVariable to explain a variable in the config (will be print as comment when
#   writting a config file)
# - See notes of read method of ConfigHelper. The behavior should be changed in the same time we implement
#   the interpolation because both need to first parse the configuration, then add the variable.
# - Add interpolation for INI format configuration (and JSON), with %{SECTION:NAME}s or %{NAME}s
# - When reading a configuration in safe mode, the type of a variable shouldn't be changed, only the value.Add test
#   for ConfigSection.update_variable and remove them from set_variable
#   -> set should overwrite the variable, update only update it's value.
#   -> Checker que créer une variable '_vars' ne fout pas le bordel avec __setatr__
 
# - Add generic type for the config classes, see https://docs.python.org/3/library/stdtypes.html#types-genericalias
# - see https://en.wikipedia.org/wiki/INI_file for more idea