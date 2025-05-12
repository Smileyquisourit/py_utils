# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The ConfigParam class
# ---------------------------------------------------------
# ./ConfigHelper/config_param.py

import re
from warnings import warn
from typing import Optional
from abc import ABC, abstractmethod

"""
======================
Module config_variable
======================

This module provides classes and utility functions for defining and parsing configuration variables 
from strings. 

Concerning the string, it supports a declarative syntax where a configuration line is represented as:

    <VariableName>[:<VariableType>]=<VariableValue>

Where :
- <VariableName> is the name of the variable, and should be a valid python name;
- <VariableType> is the type of the variable, this is optional, the default is `str`
- <VariableValue> is a string representing the variable, and will be constructed with `VariableType(VariableValue)`

The following type are currently supported:
- str
- int
- float
"""

_SUPPORTED_TYPE = {
    "str":str,
    "int":int,
    "float":float
}

_VARIABLE_NAME_RE = re.compile(r"(?P<name>[^:=\s]+)")
_VARIABLE_TYPE_RE = re.compile(r"\s*:\s*(?P<type>[^=\s]+)")
_VARIABLE_VALUE_RE = re.compile(r"\s*=\s*(?P<value>.+)")


class ConfigVariableValidator(ABC):
    """
    Abstract base class for configuration variable descriptors.

    Subclasses should implement the `validate()` method to ensure the correctness
    of any value assigned to the variable.

    Implements descriptor protocol to enable per-instance variable validation and access.
    The variable info (including value) is stored in the instance, not in the owner of the
    instance.
    """

    def __init__(self):
        super().__init__()
        self._value = None

    #def __set_name__(self,owner,name):
        # self  -> l'instance de ConfigVariableValidators ou hérité
        # owner -> La classe (et non pas l'instance) possédant l'attribut
        # name  -> Le nom de l'attribut dans la classe owner

    def __get__(self, obj, objType=None):
        return self._value
    
    def __set__(self,obj,value):
        self._value = self.validate(value)

    @abstractmethod
    def validate(self, value):
        """
            Should implement the validation logic
        """
        pass


class ConfigVariable(ConfigVariableValidator):
    """
    Implementation of a configuration variable.

    This class is a descriptor class, and supports type validation and automatic value conversion 
    on assignment.
    """

    def __init__(self, VariableName:str, VariableType:callable, value:any):
        """
        Concrete implementation of a configuration variable descriptor.

        Parameters
        ----------
        :param VariableName str: 
            Name of the configuration variable.
        :param VariableType callable: 
            A Python type (e.g. int, float, str) used for validation.
        :param value any: 
            The initial value to assign, which will be validated and converted.
        """

        self._name = VariableName
        self._type = VariableType
        self._value = self.validate(value)

    def __str__(self) -> str:
        return f"{self._name}:{self._type} = {self._value}"

    def validate(self,value:any) -> any:
        """
        Validates and converts the value using the variable's type.

        Parameters
        ----------
        :param value any:
            The new value to validate

        Return
        ------
        :return any:
            The converted value if it's valid.

        Raises
        ------
            TypeError: If the value cannot be converted to the target type.
        """
        try:
            new_value = self._type(value)
        except Exception as e:
            err_msg = f"The value {value} for variable {self._name} isn't converting to the type {self._type}!"
            raise TypeError(err_msg)
        
        # Ajouter logique pour bounds/appartenance
        return new_value

    @staticmethod
    def constructFromString(line:str) -> 'ConfigVariable':
        """
        Parses a configuration line and constructs a ConfigVariable object.

        Parameters
        ----------
        :param line str: 
            The configuration string to parse (e.g., 'port:int=8080').

        Return
        ------
        :return ConfigVariable: 
            An instance representing the parsed configuration.

        Raises
        ------
            ValueError: If parsing fails due to incorrect syntax or unsupported type.
        """

        # Extract components
        components, err_code, err_msg = _extractFromString(line)

        # Check for errors:
        if err_code != "OK":
            raise ValueError(f"({err_code}) {err_msg}")
        
        # Construct variable
        return ConfigVariable(
            VariableName = components["name"],
            VariableType = components["type"],
            value = components["value"]
            )
    

def _extractFromString(line:str) -> tuple[dict[str:any],str]:
    """
    Internal helper to extract variable name, type, and value from a configuration line.

    The expected format is: '<name>[:<type>]=<value>'

    Parameter
    ---------
    :param line str: 
        The configuration string to parse.

    Return
    ------
    :return tuple:
    - components (dict): Contains 'name', 'type', and 'value' (some may be None on failure).
    - error_code (str): "OK" on success, or a specific error code on failure.
    - error_message (str): Detailed message suitable for user feedback.
    """

    # Initialisation
    components = {
        "name": None,
        "type": None,
        "value": None
    }
    err_msg = {
        "OK": "",
        "NO_NAME_FOUND": "No name found in line '{line}'",
        'UNSUPORTED_TYPE': f"Unsuported type {{type}} in line '{{line}}', supported types are {list(_SUPPORTED_TYPE.keys())}",
        "NO_VALUE_FOUND": "No value found in line '{line}"
    }

    # Strip line:
    stripped_line = line.strip()

    # Check for the name
    if name_match := _VARIABLE_NAME_RE.match(stripped_line):
        components["name"] = name_match.group("name")
        stripped_line = stripped_line[name_match.end():]
    else:
        return (components,"NO_NAME_FOUND",err_msg["NO_NAME_FOUND"].format(line=line))
    
    # Check for the type
    if type_match := _VARIABLE_TYPE_RE.match(stripped_line):
        if not type_match.group("type") in _SUPPORTED_TYPE.keys():
            return (components,"UNSUPORTED_TYPE",err_msg["UNSUPORTED_TYPE"].format(type=type_match.group("type"),line=line))
        stripped_line = stripped_line[type_match.end():]
        components["type"] = _SUPPORTED_TYPE[type_match.group("type")]
    else :
        components["type"] = _SUPPORTED_TYPE["str"]
    
    # Check for the value
    if value_match := _VARIABLE_VALUE_RE.match(stripped_line):
        components["value"] = value_match.group("value")
    else:
        return (components,"NO_VALUE_FOUND",err_msg["NO_VALUE_FOUND"].format(line=line))
    
    return (components,"OK","")