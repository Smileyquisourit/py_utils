# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The main ConfigHelper class
# ---------------------------------------------------------
# ./ConfigHelper/confighelper.py

import os

from .config_variable import ConfigVariable
from .config_section import ConfigSection, _checkNewSection, _NO_FALLBACK

_DEFAULT_MAX_LINE = 100

class ConfigHelper():

    _DEFAULTS : ConfigSection
    _SECTIONS : dict[str:ConfigSection]

    _SUPPORTED_CONFIG_TYPE = ("str","ini")

    _comments_indicators = ["#",";"]

    @property
    def sections(self):
        return self._SECTIONS.values()

    @property
    def sections_names(self):
        return self._SECTIONS.keys()
    
    @property
    def defaults(self):
        return self._DEFAULTS.values()
    
    @property
    def defaults_names(self):
        return self._DEFAULTS.keys()


    # Constructor
    # -----------

    def __new__(cls,*args,**kwargs):
        instance = super().__new__(cls)
        object.__setattr__(instance,"_DEFAULTS",ConfigSection("DEFAULTS"))
        object.__setattr__(instance,"_SECTIONS",dict())
        return instance

    def __init__(self, comments_indicators : None|str|list[str] = None):
        
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
            raise AttributeError(f"The {name} attributes shouldn't be modified directly!")
        
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
        
        current_section = None
        for line in conf_str.splitlines():
            current_section = self._parse_line(line,current_section,safe)

    def read_ini(self, conf_file:str, safe:bool=False, max_lines:int=_DEFAULT_MAX_LINE):
        """ Check that the file exist, read all lines and pass it to read_str """
        
        # Check file:
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

                
    def read_dict(self, conf_dict:dict, safe:bool=False):
        raise NotImplementedError(f"Reading config from dict isn't implemented yet")
    
    def read_json(self, conf_file:str, safe:bool=False):
        raise NotImplementedError(f"Reading config from json file isn't implemented yet")


    # Methods to add/remove/change a section:
    # ---------------------------------------

    def add_section(self,new_section:ConfigSection):
        """ Add a section only if it isn't already in the config """

        # Check type:
        if not isinstance(new_section,ConfigSection):
            raise TypeError(f"Cannot add section of type {type(new_section)} in config!")
        
        # Check that the section isn't already present:
        if new_section._name in self._SECTIONS.keys():
            raise KeyError(f"A section nammed {new_section._name} already exist!")
        
        self._SECTIONS[new_section._name] = new_section
    
    def set_section(self,new_section:ConfigSection):
        """ Set a new section """

        # Check type:
        if not isinstance(new_section,ConfigSection):
            raise TypeError(f"Cannot add section of type {type(new_section)} in config!")
        
        self._SECTIONS[new_section._name] = new_section

    def del_section(self,section_name:str):
        """ Delete a section of the config, if it exist """

        if not section_name in self._SECTIONS.keys():
            return
        
        del self._SECTIONS[section_name]
        return

    def update_section(self,section:str|None,var:ConfigVariable):
        """ Set var to section, creating section if it doesn't exist 
        if section is None, set var in _DEFAULTS
        """

        if not section:
            self.set_default(var)
            return

        # Type conversion/check:
        if isinstance(section,ConfigSection):
            section = section._name
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
        """ Set a var to the _DEFAULTS section """

        # Type check
        if not isinstance(var,ConfigVariable):
            raise TypeError(f"Cannot update _DEFAULTS section with a variable of type {type(var)}, it should be a ConfigVariable!")
        
        # Set var in _DEFAULTS
        self._DEFAULTS.set_variable(var)


    # Methods to access sections and defaults:
    # ----------------------------------------

    def sections_items(self):
        return self._SECTIONS.items()
    
    def defaults_items(self):
        return self._DEFAULTS.items()
    
    def get(self, section:str|None, variable:str, fallback=_NO_FALLBACK):

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

        # Get variable if no section:
        if not section or not section in self.sections_names:
            return self._DEFAULTS.get(variable,fallback)
        if value := self[section].get(variable,None):
            return value
        return self._DEFAULTS.get(variable,fallback)


    # Private methods:
    # ----------------

    def _is_defined(self,var) -> bool:
        for section in self.sections:
            if var in section:
                return True
        return False         

    def _parse_line(self, line:str, current_section:None|str, safe:bool):
        """ Read one line and return the current section """

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
            
        if safe and not new_var in self[current_section]:
            raise Exception(f"New variable '{new_var._name}' in section '{current_section}' while reading config but mode safe is active")
        self.update_section(current_section, new_var)
        return current_section


