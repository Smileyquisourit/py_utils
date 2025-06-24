# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The ConfigSection base class
# ---------------------------------------------------------
# py_utils/ConfigHelper/config_section.py

"""
=====================
Module config_section
=====================

This module contain the `ConfigSection` class, that represent one section of a 
configuration file. A ConfigSection allows to access variables like an dictionary
or with attribut access, and provide a method to add default to the section. There
is also some method to add or modifie some variables to the section.

""" 

import re

from .config_variable import ConfigVariable


# Escape '[' and ']' with backslash to avoid FutureWarning (since re V3.7)
# see https://docs.python.org/3/library/re.html
_NEW_SECTION_RE = re.compile(r"\[(?P<name>.+)\]")
_NO_FALLBACK = object()


class ConfigSection(object):

    # Definition as class attributs for intellisens
    _vars: dict[str:ConfigVariable]


    # Constructor
    # -----------

    def __new__(cls, *args, **kwargs):
        # Write _vars as a instance attribute whitout using instance.__setattr__
        # as it needs the _vars variable.
        instance = super().__new__(cls)
        object.__setattr__(instance,"_vars",dict())
        return instance

    def __init__(self, name:str):
        """ Creator of ConfigSection.

        A instance of this class represent a section of a configuration file, and allow
        to access variable like a dictionary or with attribut access. When accessing a
        variable like that, only the value of the config variable is returned, not the
        actual ConfigVariable instance.

        Parameter
        ---------
        :param name: The name of the section.
        :type name: str
        """
        self._name = name


    # Dunder methods:
    # ---------------
    
    def __repr__(self):
        return f"ConfigSection {self._name} with {self.__len__()} variables"
    
    def __str__(self):
        return self.__repr__()
    
    def __len__(self) -> int:
        return len(self._vars.keys())

    def __eq__(self, other) -> bool:
        
        if not isinstance(other,ConfigSection):
            return False
        
        if self._name != other._name:
            return False
        
        return self._vars == other._vars

    # Dunder methods for accessing a variable:
    # ----------------------------------------

    def __getattribute__(self, name):

        # get the variable value if a config variable is requested
        all_vars = object.__getattribute__(self,"_vars")
        if name in all_vars.keys():
            return all_vars[name].value
        
        # Other attributes
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        
        # set the variable value if it's a config variable
        if name in self._vars.keys():
            self._vars[name].value = value
            return
        
        # Other attributes:
        object.__setattr__(self,name,value)

    def __getitem__(self, key):
        
        # The key should be a str
        if not isinstance(key,str):
            raise TypeError(f"Impossible to index section {self._name} by {key} (as type {type(key)})")
        
        if key not in self._vars.keys():
            raise KeyError(f"Variable {key} isn't in section {self._name}")
        
        return self._vars[key].value
    
    def __setitem__(self, key, value):

        # The key should be a str
        if not isinstance(key,str):
            raise TypeError(f"Impossible to index section {self._name} by {key} (as type {type(key)})")
        
        if key not in self._vars.keys():
            raise KeyError(f"Variable {key} isn't in section {self._name}")
        
        self._vars[key].value = value

    def __contains__(self,key) -> bool:

        # Accept ConfigVariable as well:
        if isinstance(key,ConfigVariable):
            key = key._name
        
        # Check that key is a str
        if not isinstance(key,str):
            return False
        
        return key in self._vars.keys()


    # Methods to add/remove/change a variable:
    # ----------------------------------------

    def add_variable(self,new_var:ConfigVariable):
        """ 
        Add a variable only if it isn't already in the section. 
        
        Parameter
        ---------
        :param new_var: The variable to add.
        :type new_var: ConfigVariable

        Raise
        -----
        :raise TypeError: When `new_var` isn't a ConfigVariable.
        :raise KeyError: When the variable already exist in the section.
        """

        # Check type:
        if not isinstance(new_var,ConfigVariable):
            raise TypeError(f"Cannot add variable of type {type(new_var)} in section {self._name}: {new_var} !!")

        # Check that the variable isn't already present:
        if new_var._name in self._vars.keys():
            raise KeyError(f"A variable named {new_var._name} already exist in section {self._name} !!")
        
        self._vars[new_var._name] = new_var
    
    def set_variable(self,new_var:ConfigVariable):
        """ Set a variable, overwritting it if it exist.
        
        Parameter
        ---------
        :param new_var: The variable to add.
        :type new_var: ConfigVariable

        Raise
        -----
        :raise TypeError: When `new_var` isn't a ConfigVariable.
        :raise KeyError: When the variable already exist in the section.
        """

        # Check type:
        if not isinstance(new_var,ConfigVariable):
            raise TypeError(f"Cannot add variable of type {type(new_var)} in section {self._name}: {new_var} !!")
        
        # Overwrite if it exist
        #object.__setattr__(self._vars,new_var._name, new_var)
        self._vars[new_var._name] = new_var

    def del_variable(self,var_name:str):
        """ Delete a variable of the section, if it exist 
        
        Parameter
        ---------
        :param var_name: The name of the variable to delete.
        :param type: str
        """

        if not var_name in self._vars.keys():
            return
        
        del self._vars[var_name]
        return
    
    def update_variable(self,new_var:ConfigVariable):
        """ 
        Set a new variable only if it exist. Raise an error
        if the variable isn't in the section.
        
        Parameter
        ---------
        :param new_var: The variable to update.
        :type new_var: ConfigVariable

        Raise
        -----
        :raise TypeError: When `new_var` isn't a ConfigVariable.
        """

        # Check type:
        if not isinstance(new_var,ConfigVariable):
            raise TypeError(f"Cannot update variable of type {type(new_var)} in section {self._name}: {new_var} !!")
        
        if not new_var._name in self._vars.keys():
            raise KeyError(f"The variable {new_var} isn't in the section {self._name}")
        
        # CHANGED
        self._vars[new_var._name].value = new_var.value

    def with_defaults(self,default_section:'ConfigSection') -> 'ConfigSection':
        """ 
        Method to add some default variables to a new instance of ConfigSection. 
        
        This method is intended to be used by a ConfigHelper instance, when
        accessing a section. The new ConfigSection has the same name as this instance,
        but some default variable are added (only) if they didn't exist in this instance.

        Parameter
        ---------
        :param default_section: An other ConfigSection with default variables.
        :type default_section: ConfigSection

        Return
        ------
        :return: A ConfigSection contening all the variable of this section, and the one of the
            default section if they doesn't exist in this one.
        :rtype: ConfigSection

        Raise
        -----
        :raise TypeError: When `default_section` isn't a ConfigSection.
        """

        # Check type:
        if not isinstance(default_section,ConfigSection):
            raise TypeError(f"Cannot set default in section {self._name} without an other ConfigSection!! I've received a {type(default_section)} !!")

        # Create and populate new section with default variables
        new_section = ConfigSection(self._name)
        for var in default_section.values():
            new_section.set_variable(var)

        # Overwrite with this instance variables
        for var in self.values():
            new_section.set_variable(var)
                
        
        return new_section


    # Methods to access variables:
    # ----------------------------

    def items(self):
        """ Returns a tuple containing tuples of (keys, values). """
        return tuple(self._vars.items())
    
    def keys(self):
        """  Returns a tuple containing the keys in the section.  """
        return tuple(self._vars.keys())
    
    def values(self):
        """  Returns a tuple containing the variables in the section.  """
        return tuple(self._vars.values())
    
    def get(self, key:str, fallback:any=_NO_FALLBACK):
        """
        Retrieve the value of an individual variable of the section. It will raise
        a KeyError if the variable isn't in the config and no fallback are provided,
        or return the fallback if there is one.

        Parameters
        ----------
        :param key: The name of the variable to retreive.
        :type key: str

        :param fallback: The fallback value to return if the key isn't present.
        :type fallback: any

        Return
        ------
        :return: The value of the variable.
        :rtype: any

        Raise
        -----
        :raise TypeError: When the key isn't a string.
        :raise KeyError: When the variable isn't in the section, and no fallback are provided.
        """

        # Check key is a string:
        if not isinstance(key,str):
            raise TypeError(f"Impossible to index section {self._name} by {key} (as type {type(key)})")
        
        if not key in self._vars.keys():

            if fallback is _NO_FALLBACK:
                raise KeyError(f"Variable {key} isn't in section {self._name}")
                            
            else:
                return fallback                
        
        return self._vars[key].value


def _checkNewSection(line:str) -> str|None:
    """
    Return the name of the section if the line correpsond to a section definition
    in ini format, else None.
    """

    # Type check:
    if not isinstance(line,str):
        raise TypeError(f"Can't check if new section with line as {type(line)}")

    if section_name := _NEW_SECTION_RE.fullmatch( line.strip() ):
        return section_name.group('name')
    return None

