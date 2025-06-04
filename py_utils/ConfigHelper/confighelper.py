# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The main ConfigHelper class
# ---------------------------------------------------------
# ./ConfigHelper/confighelper.py

"""
===================
Module configHelper
===================

This module contains the ConfigHelper class, which represents a configuration. 
This class provides methods to read a configuration from different formats:
- A modified INI format
- A JSON format


Modified INI format
--------------------
A plain-text format in which each line follows the form:

    <VariableName>[:<VariableType>]=<VariableValue>

Here, the VariableType is optional (default is `str`). Arbitrary whitespace 
between elements is allowed, but the order cannot be changed. Comments explaining 
the variables can be added, but they must be on separate lines. By default, comment 
delimiters are ';' and '#', although these can be changed.


JSON format
------------
A JSON format where the top-level dictionary must contain two keys: 'DEFAULTS' and 'SECTIONS'. 
- 'DEFAULTS' should be a dictionary representing a section containing all default variables 
  shared by all sections.
- 'SECTIONS' should be a list of dictionaries, each representing a section.

A section dictionary should contain a single key (the section name) and its value should 
be a list of dictionaries, each representing a variable.

A variable dictionary must contain at least the keys 'name' and 'value'. Optionally, it can 
also contain a 'type' key. The 'name' must be a string, the 'value' should also be a string 
(currently, type validation is not enforced). The 'type' can be a supported type name as a 
string (e.g., 'int', 'float', and 'bool'), or a class (which must have a '__name__' attribute).
"""


import os
import json

from .config_variable import ConfigVariable
from .config_section import ConfigSection, _checkNewSection, _NO_FALLBACK

_DEFAULT_MAX_LINE = 100

class ConfigHelper():

    _DEFAULTS : ConfigSection
    _SECTIONS : dict[str:ConfigSection]

    _SUPPORTED_CONFIG_TYPE = ("str","dict","ini","json")

    _comments_indicators = ("#",";")

    @property
    def sections(self):
        """ A view on the ConfigSection in this config. """
        return self._SECTIONS.values()

    @property
    def sections_names(self):
        """ A view on the name of the sections in this config """
        return self._SECTIONS.keys()
    
    @property
    def defaults(self):
        """ A view on the default values in this config. """
        return self._DEFAULTS.values()
    
    @property
    def defaults_names(self):
        """ A view on the values of the sections in this config """
        return self._DEFAULTS.keys()


    # Constructor
    # -----------

    def __new__(cls,*args,**kwargs):
        instance = super().__new__(cls)
        object.__setattr__(instance,"_DEFAULTS",ConfigSection("DEFAULTS"))
        object.__setattr__(instance,"_SECTIONS",dict())
        return instance

    def __init__(self, comments_indicators : None|str|list[str] = None):
        """
        Initialize a ConfigHelper instance.

        This class provides functionality to read and manage configuration files, 
        supporting a modified INI format and a JSON format. It can parse configuration 
        files, store variables and sections, and apply default variables across sections.

        Parameters
        ----------
        :param comments_indicators: The character(s) used to identify comment lines in the 
            INI format. By default, comments are identified using ';' and '#'. This parameter 
            allows customization of the comment indicators to fit different needs.
        :type comments_indicators: None | str | list[str], optional
        """

        if comments_indicators:
            self._comments_indicators = comments_indicators


    # Dunder methods:
    # ---------------

    def __repr__(self):
        return f"ConfiHelper with {self.__len__()} variables"
    
    def __str__(self):
        return self.__repr__()
    
    def __len__(self) -> int:
        _len = 0
        for section in self.sections:
            _len += len(section)

        for var in self.defaults_names:
            if not self._is_defined(var):
                _len += 1

        return _len
    

    # Dunder methods for accessing a variable or a section:
    # -----------------------------------------------------

    def __getattribute__(self, name):

        # Get the section if a config section is requested
        all_sections = object.__getattribute__(self,"_SECTIONS")
        if name in all_sections.keys():
            return all_sections[name]
        
        # Get the variable if a config variable is requested
        defaults = object.__getattribute__(self,"_DEFAULTS")
        if name in defaults.keys():
            return defaults[name]
        
        # Other attributes
        return object.__getattribute__(self, name)
    
    def __setattr__(self, name, value):
        
        # Protect _DEFAULTS and _SECTIONS
        if name in ("_DEFAULTS","_SECTIONS"):
            raise AttributeError(f"The {name} attribute shouldn't be modified directly!")
        
        # Normal behavior
        object.__setattr__(self,name,value)

    def __getitem__(self,key):

        # The key should be a str
        if not isinstance(key,str):
            raise TypeError(f"Impossible to index config by {key} (as type {type(key)})")

        if key not in self._SECTIONS.keys():
            if key in self._DEFAULTS.keys():
                return self._DEFAULTS[key]
            raise KeyError(f"Section or param {key} isn't in config")
        
        return self._SECTIONS[key].with_defaults(self._DEFAULTS)
    
    def __setitem__(self, key, value):
        
        raise AttributeError(f"Setting from bracket indexing isn't allowed!")

    def __contains__(self,key) -> bool:
        
        # Accept ConfigVariable and ConfigSection as well:
        if isinstance(key,(ConfigVariable,ConfigSection)):
            key = key._name

        # Check that key is str
        if not isinstance(key,str):
            return False
        
        if not self._is_defined(key):
            return key in self._DEFAULTS.keys()
        return True


    # Methods for reading a config:
    # -----------------------------

    def read(self, conf_obj:any, type:any):
        pass
    def read_safe(self, conf_obj, type, default_conf, default_type):
        pass

    def read_str(self, conf_str:str, safe:bool=False):
        """
        Parse a configuration from a string in the modified INI format.

        Parameters
        ----------
        :param conf_str: The configuration content as a single string (with line breaks 
            separating entries).
        :type conf_str: str

        :param safe: If True, raises an error if unknown sections or variables are encountered.
            If False (default), unknown sections or variables are accepted.
        :type safe: bool
        """
        
        current_section = None
        for line in conf_str.splitlines():
            current_section = self._parse_line(line,current_section,safe)

    def read_ini(self, conf_file:str, safe:bool=False, max_lines:int=_DEFAULT_MAX_LINE):
        """
        Parse a configuration from a file in the modified INI format.
     
        Parameters
        ----------
        :param conf_file: Path to the configuration file.
        :type conf_file; str | bytes | os.PathLike | int

        :param safe:  If True, raises an error if unknown sections or variables are encountered.
            If False (default), unknown sections or variables are accepted.
        :type safe: bool

        :param max_lines: The maximum number of lines to read from the file, to prevent excessive 
            memory usage. Default to 100.
        :type max_lines: int
     
        Raises
        ------
        :raise TypeError: If `conf_file` is not a valid file path type.
        :raise FileNotFoundError: If the configuration file does not exist.
        :raise PermissionError: If the configuration file cannot be opened for reading.
        :raise Exception: If the file exceeds `max_lines` or if the safe mode check fails.
        """
        
        # Check file:
        if not isinstance(conf_file,(str,bytes,os.PathLike,int)):
            raise TypeError(f"The configuration file should be string, bytes, os.PathLike or integer, not {type(conf_file)}")
        if not os.path.isfile(conf_file):
            raise FileNotFoundError(f"The config file '{conf_file}' wasn't found!")
        if not os.access(conf_file, os.R_OK):
            raise PermissionError(f"The config file '{conf_file}' was found, but can't be open in read mode!")
        
        # Read file:
        nLigne = 0
        with open(conf_file,'r') as f:
            current_section = None
            for line in f:

                # Check number of line
                if nLigne > max_lines:
                    raise Exception(f"Max number of ligne ({max_lines}) was read in file {conf_file}")

                # Parse line
                current_section = self._parse_line(line,current_section,safe)
                nLigne += 1

                
    def read_dict(self, conf_dict:dict, safe:bool=False) -> None:
        """
        Parse a configuration from a dictionary in JSON-like format.

        Notes
        -----
        This method expects the dictionary to be structured as:
          - 'DEFAULTS': list of default variables (optional)
          - 'SECTIONS': list of sections, each as a dict with a single key (the section name) 
            and a list of variables.

        Parameters
        ----------
        :param conf_dict: The configuration as a dictionary, with 'DEFAULTS' and 'SECTIONS' 
            keys.
        :type conf_dict: dict

        :param safe: If True, raises an error if unknown sections or variables are encountered.
            If False (default), unknown sections or variables are accepted.
        :type safe: bool, optional

        Raises
        ------
        :raise TypeError: When `conf_dict` is not a dictionary or if sections are incorrectly 
            defined.
        :raise ValueError: When required keys are missing or sections are not properly structured.
        """
        
        # Type check
        if not isinstance(conf_dict,dict):
            raise TypeError(f"Cannot read {conf_dict} as a dict, as it is a {type(conf_dict)}")
        
        # Read defaults if their is any
        if default_section := conf_dict.get("DEFAULTS",None):
            self._parse_dict(None,default_section,safe)

        # Read list of sections_dict
        if not (sections_list := conf_dict.get("SECTIONS",None)):
            raise ValueError("No SECTIONS found conf_dict")
        if not isinstance(sections_list,list):
            raise TypeError(f"SECTIONS uncorrectly defined! It should be a list, instead I've received a {type(sections_list)}.")
        
        # Parse each section_dict
        for section_dict in sections_list:
            # A section should be in the form {'section_name':[{var1},{var2},...]}

            # Type check
            if not isinstance(section_dict,dict):
                raise TypeError(f"A section was uncorrectly defined, it should be a dict but I've received a {type(section_dict)}")
            if len(section_dict) != 1:
                raise ValueError(f"A section should be defined as a dict with only one key/value pair, instead I've received {section_dict}")
            
            # Construct section
            for section_name, section_vars in section_dict.items():
                self._parse_dict(section_name, section_vars, safe)
    
    def read_json(self, conf_file:str, safe:bool=False) -> None:
        """
        Parse a configuration from a JSON file.

        Parameters
        ----------
        :param conf_file: Path to the JSON configuration file.
        :type conf_file: str, bytes, os.PathLike or int

        :param safe: If True, raises an error if unknown sections or variables are encountered.
            If False (default), unknown sections or variables are accepted.
        :type safe: bool

        Raises
        ------
        :raise TypeError: When `conf_file` is not a valid file path type.
        :raise FileNotFoundError: When the configuration file does not exist.
        :raise PermissionError: When the configuration file cannot be opened for reading.
        :raise json.JSONDecodeError: When the JSON content is invalid.
        :raise Exception: When the safe mode check fails.
        """

        # Check file:
        if not isinstance(conf_file,(str,bytes,os.PathLike,int)):
            raise TypeError(f"The configuration file should be string, bytes, os.PathLike or integer, not {type(conf_file)}")
        if not os.path.isfile(conf_file):
            raise FileNotFoundError(f"The config file '{conf_file}' wasn't found!")
        if not os.access(conf_file, os.R_OK):
            raise PermissionError(f"The config file '{conf_file}' was found, but can't be open in read mode!")
        
        # Read file:
        with open(conf_file,'r') as f:
            conf_dict = json.load(f)
        self.read_dict(conf_dict,safe)


    # Methods to add/remove/change a section:
    # ---------------------------------------

    def add_section(self,new_section:ConfigSection):
        """
        Add a new section to the configuration if it does not already exist.

        Parameters
        ----------
        :param new_section: The section to add.
        :type new_section: ConfigSection

        Raises
        ------
        :raise TypeError: When `new_section` is not a ConfigSection.
        :raise KeyError: When a section with the same name already exists.
        """

        # Check type:
        if not isinstance(new_section,ConfigSection):
            raise TypeError(f"Cannot add section of type {type(new_section)} in config!")
        
        # Check that the section isn't already present:
        if new_section._name in self._SECTIONS.keys():
            raise KeyError(f"A section nammed {new_section._name} already exist!")
        
        self._SECTIONS[new_section._name] = new_section
    
    def set_section(self,new_section:ConfigSection):
        """
        Add or replace a section in the configuration.

        Parameters
        ----------
        :param new_section: The section to add or replace.
        :type new_section: ConfigSection

        Raises
        ------
        :raise TypeError: When `new_section` is not a ConfigSection.
        """

        # Check type:
        if not isinstance(new_section,ConfigSection):
            raise TypeError(f"Cannot add section of type {type(new_section)} in config!")
        
        self._SECTIONS[new_section._name] = new_section

    def del_section(self,section_name:str):
        """
        Remove a section from the configuration if it exists.

        Parameters
        ----------
        :param section_name: The name of the section to remove.
        :type section_name: str

        Notes
        -----
        If the section does not exist, no action is taken.
        """

        if not section_name in self._SECTIONS.keys():
            return
        
        del self._SECTIONS[section_name]
        return

    def update_section(self,section:str|None,var:ConfigVariable):
        """
        Add or update a variable in the given section, creating the section if necessary.

        If `section` is None, the variable is added to the defaults section.

        Parameters
        ----------
        :param section: The name of the section to update. If None, the variable is added to the defaults.
        :type section: str or None

        :param var : The variable to add or update.
        :type var: ConfigVariable

        Raises
        ------
        :raise TypeError: When `section` is not a string or None, or if `var` is not a ConfigVariable.
        """

        if not section:
            self.set_default(var)
            return

        # Type check:
        if not isinstance(section, str):
            raise TypeError(f"Cannot update section of type {type(section)} in config!")
        if not isinstance(var,ConfigVariable):
            raise TypeError(f"Cannot update section with a variable of type {type(var)}, it should be a ConfigVariable!")
        
        # Create section if needed:
        if not section in self.sections_names:
            self._SECTIONS[section] = ConfigSection(section)
        
        # Set var in section:
        self._SECTIONS[section].set_variable(var)

    def set_default(self,var:ConfigVariable):
        """
        Add or update a variable in the defaults section.

        Parameters
        ----------
        :param var: The variable to add or update in the defaults section.
        :type var: ConfigVariable

        Raises
        ------
        :raise TypeError: When `var` is not a ConfigVariable.
        """

        # Type check
        if not isinstance(var,ConfigVariable):
            raise TypeError(f"Cannot update _DEFAULTS section with a variable of type {type(var)}, it should be a ConfigVariable!")
        
        # Set var in _DEFAULTS
        self._DEFAULTS.set_variable(var)


    # Methods to access sections and defaults:
    # ----------------------------------------

    def sections_items(self):
        """
        Get a set-like over (section_name, ConfigSection) pairs.

        Returns
        -------
        :return: An iterator over (section_name, ConfigSection) pairs.
        :rtype: iterator
        """
        return self._SECTIONS.items()
    
    def defaults_items(self):
        """
        Get an iterator over (variable_name, ConfigVariable) pairs from the defaults section.

        Returns
        -------
        :return: An iterator over (variable_name, ConfigVariable) pairs.
        :rtype: dictionary view
        """
        return self._DEFAULTS.items()
    
    def get(self, section:str|None, variable:str, fallback=None):
        """
        Get the value of a variable from a specific section or from the defaults if not found.
        If the value isn't found in the section or in the default value, the fallback (if provieded)
        is returned. When no fallback is provieded and the variable isn't found, 

        Parameters
        ----------
        :param section: The name of the section to search in. If None or not found, defaults are used.
        :type section: str or None

        :param variable: The name of the variable to retrieve.
        :type variable: str
            
        :param fallback: The fallback value if the variable is not found (default to None).
        :type fallback: any
            

        Returns
        -------
        :return: The value of the variable if found, otherwise the fallback.
        :rtype: any

        Raises
        ------
        :raise TypeError: If `section` is not str or None, or if `variable` is not str.
        """

        # Type conversion
        if section and isinstance(section,ConfigSection):
            section = section._name
        if isinstance(variable,ConfigVariable):
            variable = variable._name
        
        # Type check
        if section and not isinstance(section,str):
            raise TypeError(f"Impossible to index section of conf by key of type {type(section)}")
        if not isinstance(variable,str):
            raise TypeError(f"Impossible to index variable of conf by key of type {type(section)}")

        # Get variable  if no section:
        if not section or not section in self.sections_names:
            return self._DEFAULTS.get(variable,fallback)
        if value := self[section].get(variable,_NO_FALLBACK) == _NO_FALLBACK:
            return value
        return self._DEFAULTS.get(variable,fallback)


    # Private methods:
    # ----------------

    def _is_defined(self,var) -> bool:
        """
        Check whether a configuration variable is defined in any of the sections.

        This method iterates through all sections in the configuration and returns 
        True as soon as the variable is found.

        Parameters
        ----------
        :param var: The name of the variable to check for, or a ConfigVariable instance 
            whose name will be used.
        :type var: str | ConfigVariable

        Returns
        -------
        :return: True if the variable exists in any section, False otherwise.
        :rtype: bool
        """
        for section in self.sections:
            if var in section:
                return True
        return False

    def _parse_line(self, line:str, current_section:None|str, safe:bool) -> str|None:
        """
        Parse a single line from the configuration file and update the relevant section.

        This method handles:
        - Skipping empty lines or comment lines.
        - Detecting the start of a new section.
        - Creating or updating configuration variables.

        Parameters
        ----------
        :param line: The line to parse.
        :type line: str

        :param current_section: The name of the current section being parsed. If None, the line is 
            considered part of the defaults.
        :type current_section: str | None

        :param safe: If True, only existing sections and variables (from a predefined template) can 
            be modified, and an exception is raised if an unknown section or variable is encountered.
        :type safe: bool

        Returns
        -------
        :return: The updated current section name, or None if no section was detected (still defaults).
        :rtype: str | None

        Raises
        ------
        :raise Exception: When a new section or variable is encountered in safe mode. 
        """

        # Strip line and ignore comments or empty line
        line = line.lstrip()
        if not line or line[0] in self._comments_indicators:
            return current_section
        
        # Check start of a new section
        if new_section := _checkNewSection(line):
            if safe and not (new_section in self.sections_names) :
                raise Exception(f"New section {new_section} while reading config but mode safe is active (known section: {self.sections_names})")
            return new_section
        
        # Create new var:
        new_var = ConfigVariable.constructFromString(line)

        if not current_section:
            # We are still reading defaults from the config
            if safe and not new_var in self._DEFAULTS:
                raise Exception(f"New default variable '{new_var._name}' while reading config but mode safe is active (knowned defaults: {self.defaults_names})")
            
        elif safe and not new_var in self[current_section]:
            raise Exception(f"New variable '{new_var._name}' in section '{current_section}' while reading config but mode safe is active")
        
        self.update_section(current_section, new_var)
        return current_section

    def _parse_dict(self,key:str|None,value:list[dict],safe:bool) -> None:
        """
        Parse a dictionary representation of a configuration section and update its variables.

        This method is used when reading a configuration from JSON format, where each 
        section is represented by a list of dictionaries defining variables.

        Parameters
        ----------
        :param key:  The name of the section being parsed. If None, the variables are considered 
            part of the defaults section.
        :type key: str | None

        :param value: A list of dictionaries, each containing the definition of a variable (name, 
            value, and optionally type).
        :type value: list[dict]

        :param safe: If True, only existing variables in the section or defaults can be modified. 
            An exception is raised if an unknown variable is encountered.
        :type safe: bool

        Raises
        ------
        :raise Exception: When encountering a new variable in safe mode.
        """
        
        # Check section name:
        if safe and not key in self.sections_names:
            raise Exception(f"A new section nammed '{key}' was encourenterd in safe mode!")
        section = key

        # Update section
        for var_dict in value:

            new_var = ConfigVariable.constructFromDict(var_dict)

            if not section:
                # We are still reading defaults from the config
                if safe and not new_var in self._DEFAULTS:
                    raise Exception(f"New default variable '{new_var._name}' while reading config but mode safe is active (knowned defaults: {self.defaults_names})")
            
            elif safe and not new_var in self[section]:
                raise Exception(f"New variable '{new_var._name}' in section '{section}' while reading config but mode safe is active")
            
            self.update_section(section,new_var)



