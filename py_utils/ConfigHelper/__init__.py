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
default variables, which are shared across all sections.

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

# - Add generic type for the config classes, see https://docs.python.org/3/library/stdtypes.html#types-genericalias
# - see https://en.wikipedia.org/wiki/INI_file for more idea