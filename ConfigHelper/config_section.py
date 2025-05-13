# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The ConfigSection base class
# ---------------------------------------------------------
# ./ConfigHelper/config_section.py

from .config_variable import ConfigVariable

class ConfigSection(object):

    _vars: dict[str:ConfigVariable] = dict()

    def __init__(self, name:str):
        self._name = name
        self._vars: dict[str:ConfigVariable] = dict()
        #self._parentConfig for accessing default value ?


    # Dunder methods:
    # ---------------
    
    def __repr__(self):
        return f"ConfigSection {self._name} with {self.__len__()} variables"
    
    def __str__(self):
        return self.__repr__()
    
    def __len__(self) -> int:
        return len(self._vars.keys())


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
        """ Add a variable only if it isn't already in the section. """

        # Check type:
        if not isinstance(new_var,ConfigVariable):
            raise TypeError(f"Cannot add variable of type {type(new_var)} in section {self._name}: {new_var} !!")

        # Check that the variable isn't already present:
        if new_var._name in self._vars.keys():
            raise KeyError(f"A variable named {new_var._name} already exist in section {self._name} !!")
        
        self._vars[new_var._name] = new_var
    
    def set_variable(self,new_var:ConfigVariable):
        """ Set a new variable """

        # Check type:
        if not isinstance(new_var,ConfigVariable):
            raise TypeError(f"Cannot add variable of type {type(new_var)} in section {self._name}: {new_var} !!")
        
        self._vars[new_var._name] = new_var

    def del_variable(self,var_name:str):
        """ Delete a variable of the section, if it exist """

        if not var_name in self._vars.keys():
            return
        
        del self._vars[var_name]
        return
    
