# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The ConfigParam class
# ---------------------------------------------------------
# py_utils/ConfigHelper/config_param.py


"""
======================
Module config_variable
======================

This module provides classes and utility functions for defining and parsing configuration variables 
from strings and dictionary. 

Concerning the string, it supports a declarative syntax where a configuration line is represented as:

    <VariableName>[:<VariableType>]=<VariableValue>

Concerning the dictionary, it should contain a 'name' and 'value' key, and optionaly a 'type' key. The 
'name' value should be a str, the 'value' should also be a string, but type validation isn't enforced yet. 
As for the 'type', it should be a type or have an attribute '__name__' and be a supported one.

Where :
- <VariableName> is the name of the variable, and should be a valid python name;
- <VariableType> is the type of the variable, this is optional, the default is `str`
- <VariableValue> is a string representing the variable, and will be constructed with `VariableType(VariableValue)`

The following type are currently supported:
- `str`
- `int`
- `float`
- `bool`
"""

import re
import functools

from .config_exceptions import ConfigConversionError

# Conversion functionality:
# -------------------------

def _convert_str(value:any,cVarName,cVarType) -> str:
    try:
        new_value = str(value)
    except Exception as e:
        raise ConfigConversionError(f"[ConfigVariable '{cVarName}'] Error while trying to convert '{value}' to {cVarType}:\n{e}")
    return new_value
def _convert_int(value:any,cVarName,cVarType) -> int:
    try:
        new_value = int(value)
    except Exception as e:
        raise ConfigConversionError(f"[ConfigVariable '{cVarName}'] Error while trying to convert '{value}' to {cVarType}:\n{e}")
    return new_value
def _convert_float(value:any,cVarName,cVarType) -> float:
    try:
        new_value = float(value)
    except Exception as e:
        raise ConfigConversionError(f"[ConfigVariable '{cVarName}'] Error while trying to convert '{value}' to {cVarType}:\n{e}")
    return new_value
def _convert_bool(value:any,cVarName,cVarType) -> bool:

    # Try to convert first to str:
    try:
        value = str(value)
    except Exception as e:
        raise ConfigConversionError(f"[ConfigVariable '{cVarName}'] Error while trying to convert '{value}' to {cVarType}:\n{e}")
    
    # From string deduct boolean value:
    if value in ("true","True","1","on","yes"):
        return True
    if value in ("false","False","0","off","no"):
        return False
    raise ConfigConversionError(f"Impossible to deduct a boolean value from '{value}'")

_SUPPORTED_TYPE = {
    "str"  : str,
    "int"  : int,
    "float": float,
    "bool" : bool
}
_CONVERSION_FUNC = {
    str  : _convert_str,
    int  : _convert_int,
    float: _convert_float,
    bool : _convert_bool
}

_VARIABLE_NAME_RE = re.compile(r"(?P<name>[^:=\s]+)")
_VARIABLE_TYPE_RE = re.compile(r"\s*:\s*(?P<type>[^=\s]+)")
_VARIABLE_VALUE_RE = re.compile(r"\s*=\s*(?P<value>.+)")

class ConfigVariable(object):
    """
    Implementation of a configuration variable.
 
    This class represent one variable of a configuration, and supports type validation and automatic value conversion 
    on assignment. The verification and conversion logic is done by properties.

    Once the type was set a first time (during initialisation of the instance), it can't be changed !!
    """

    @property
    def value(self) -> any:
        """ The value of the variable. """
        return self._value
     
    @value.setter
    def value(self,new_value):
        self._value = self._validate_value(new_value)


    @property
    def type(self) -> any:
        """ The type of the variable. """
        return self._type
    
    @type.setter
    def type(self,new_type):
        raise AttributeError(f"Impossible to change type to {new_type} after initialisation !")

    
    # Dunder methods
    # --------------

    def __init__(self, VariableName:str, VariableType:callable, value:any):
        """
        Concrete implementation of a configuration variable. The conversion of the value is done in the 
        constructor, and will raise an error if it isn't valid.
 
        Parameters
        ----------
        :param VariableName: Name of the configuration variable.
        :type VariableName: str

        :param VariableType: A Python type (e.g. int, float, str) used for validation.
        :type VariableType: type

        :param value: The initial value to assign, which will be validated and converted.
        :type value: any

        Raises
        ------
        :raise ValueError: If the type is not supported.
        :raise TypeError: If the value cannot be converted to the wanted type.
        """
 
        self._name = VariableName
        self._type = self._validate_type(VariableType)
        self._value = self._validate_value(value)

    def __repr__(self):
        return f"{self._name}:{self._type.__name__} = {self._value}"
 
    def __str__(self) -> str:
        return self.__repr__()
 
    def __eq__(self, other) -> bool:
        
        if not isinstance(other,ConfigVariable):
            return False
        
        return \
            self._name == other._name and \
            self._type == other._type and \
            self._value == other._value

    # Private methods
    # ---------------

    def _validate_value(self,new_value:any) -> any:
        """
        Validates and converts the value using the variable's type.
 
        Parameters
        ----------
        :param value: The new value to validate
        :type value: any
 
        Return
        ------
        :return: The converted value if it's valid.
        :rtype: any
 
        Raises
        ------
        :raise TypeError: If the value cannot be converted to the target type.
        """
        try:
            correct_value = _CONVERSION_FUNC[self._type](new_value,self._name,self._type)
        except KeyError as e:
            err_msg = f"No conversion function found for type '{self._type.__name__}', supported type are {_SUPPORTED_TYPE}.\n"
            err_msg += "Maybe your conversion function wasn't registered before the config was read ?\n"
            err_msg += str(e)
            raise KeyError(err_msg)
         
        return correct_value

    def _validate_type(self,new_type:any) -> callable:
        """
        Validate the given type, and if it's a string return the corresponding type.

        Parameters
        ----------
        :param new_type: The new type to validate.
        :type new_type: type
        
        Return
        ------
        :return: The corresponding type if it's valid.
        :rtype: type

        Raises
        ------
        :raise ValueError: If the type is not supported.
        """

        if isinstance(new_type,str):
            if not new_type in _SUPPORTED_TYPE.keys():
                raise ValueError(f"The type '{new_type}' isn't supported.")
            return _SUPPORTED_TYPE[new_type]
        
        if not new_type in _SUPPORTED_TYPE.values():
            raise ValueError(f"The type '{type(new_type).__name__}' isn't supported.")
        return new_type


    # Static methods
    # --------------

    @staticmethod
    def constructFromString(line:str) -> 'ConfigVariable':
        """
        Parses a configuration line and constructs a ConfigVariable object.
 
        Parameters
        ----------
        :param line: The configuration string to parse (e.g., 'port:int=8080').
        :type line: str
 
        Return
        ------
        :return: An instance representing the parsed configuration.
        :rtype: ConfigVariable
 
        Raises
        ------
        :raise ValueError: If parsing fails due to incorrect syntax or unsupported type.
        """
 
        # Extract components:
        components, err_code, err_msg = _extractFromString(line)
 
        # Check for errors:
        if err_code != "OK":
            raise ValueError(f"({err_code}) {err_msg}")
         
        # Construct variable:
        return ConfigVariable(
            VariableName = components["name"],
            VariableType = components["type"],
            value = components["value"]
            )

    @staticmethod
    def constructFromDict(var_dict:dict[str:str]) -> 'ConfigVariable':
        """ Create a ConfigVariable from a dictionary.

        The dict should contain values as string, and the following keys:
        - `'name'` -> the name of the variable
        - `'type'` -> the type of the variable
        - `'value'` -> the value of the variable
        
        Parameter
        ---------
        :param var_dict: The dict in wich to extract the name, type, and value of the 
            wanted variable.
        :type var_dict: dict[str:str]

        Return
        ------
        :return: An instance representing the parsed configuration.
        :rtype: ConfigVariable
 
        Raises
        ------
        :raise ValueError: If parsing fails due to incorrect syntax or unsupported type.
        """

        # Extract components:
        components, err_code, err_msg = _extractFromDict(var_dict)

        # Check for errors:
        if err_code != "OK":
            raise ValueError(f"({err_code}) {err_msg}")
        
        # Construct variable:
        return ConfigVariable(
            VariableName = components["name"],
            VariableType = components["type"],
            value = components["value"]
        )

    @staticmethod
    def register(varType:type):
        """ Register a new type with it's corresponding conversion function.

        The new type should be a class, and it will be register under it's name, obtained
        with `varType.__name__`, while the decorated function will be registered under 
        `varType`

        Parameter
        ---------
        :param varType: The new type to register.
        :type varType: type
        """

        def decorator(func):

            # Wrap user func
            @functools.wraps(func)
            def wrapper(new_value,cVarName,cVarType):
                try:
                    value = func(new_value)
                except Exception as e:
                    raise ConfigConversionError(f"[ConfigVariable '{cVarName}'] Error while trying to convert '{new_value}' to {cVarType}:\n{e}")

                return value

            # Register func
            _SUPPORTED_TYPE[varType.__name__] = varType
            _CONVERSION_FUNC[varType] = wrapper
            return wrapper
        return decorator



def _extractFromString(line:str) -> tuple[dict[str:any],str]:
    """ Internal helper to extract variable name, type, and value from a configuration line.

    The expected format is: '<name>[:<type>]=<value>'

    Parameter
    ---------
    :param line str: 
        The configuration string to parse.

    Return
    ------
    :return: The following tupple
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
        "NO_VALUE_FOUND": "No value found in line '{line}'"
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

def _extractFromDict(_dict:dict) -> tuple[dict[str:any],str]:
    """ Internal helper to extract variable name, type, and value from a dict.

    A dictionary representing a configuration variable should contain a 'name' and
    'value' key, and optionaly a 'type' key. The 'name' value should be a str, the 
    'value' should also be a string, but type validation isn't enforced yet. As for 
    the 'type', it should be a type or have an attribute '__name__' and be a supported
    one.

    Parameter
    ---------
    :param _dict: The dict to parse.
    :type _dict: dict

    Return
    ------
    :return: The following tupple
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
        "NO_NAME_FOUND": "No name found in dict!",
        'UNSUPORTED_TYPE': f"Unsuported type {{type}} in line dict, supported types are {list(_SUPPORTED_TYPE.keys())}",
        "NO_VALUE_FOUND": "No value found in dict!"
    }

    # Check name
    if not (name := _dict.get("name",None)):
        return (components,"NO_NAME_FOUND",err_msg["NO_NAME_FOUND"])
    components["name"] = name

    # Check type
    _type = _dict.get("type","str")
    if not isinstance(_type,str):
        try:
            _type = _type.__name__
        except:
            return (components,"UNSUPORTED_TYPE",err_msg["UNSUPORTED_TYPE"].format(type=_type))
    if not _type in _SUPPORTED_TYPE.keys():
        return (components,"UNSUPORTED_TYPE",err_msg["UNSUPORTED_TYPE"].format(type=_type))
    components["type"] = _SUPPORTED_TYPE[_type]

    # Check value
    if not (value := _dict.get("value",None)):
        return (components,"NO_VALUE_FOUND",err_msg["NO_VALUE_FOUND"])
    components["value"] = value

    return (components,"OK","")







# Old implemntation as desciptors:
# ================================
#### class ConfigVariableValidator(ABC):
####     """
####     Abstract base class for configuration variable descriptors.
#### 
####     Subclasses should implement the `validate()` method to ensure the correctness
####     of any value assigned to the variable.
#### 
####     Implements descriptor protocol to enable per-instance variable validation and access.
####     The variable info (including value) is stored in the instance, not in the owner of the
####     instance.
####     """
#### 
####     def __init__(self):
####         super().__init__()
####         self._value = None
#### 
####     #def __set_name__(self,owner,name):
####         # self  -> l'instance de ConfigVariableValidators ou hérité
####         # owner -> La classe (et non pas l'instance) possédant l'attribut
####         # name  -> Le nom de l'attribut dans la classe owner
#### 
####     def __get__(self, obj, objType=None):
####         return self._value
####     
####     def __set__(self,obj,value):
####         self._value = self.validate(value)
#### 
####     @abstractmethod
####     def validate(self, value):
####         """
####             Should implement the validation logic
####         """
####         pass
#### 
#### 
#### class ConfigVariable(ConfigVariableValidator):
####     """
####     Implementation of a configuration variable.
#### 
####     This class is a descriptor class, and supports type validation and automatic value conversion 
####     on assignment.
####     """
#### 
####     def __init__(self, VariableName:str, VariableType:callable, value:any):
####         """
####         Concrete implementation of a configuration variable descriptor.
#### 
####         Parameters
####         ----------
####         :param VariableName str: 
####             Name of the configuration variable.
####         :param VariableType callable: 
####             A Python type (e.g. int, float, str) used for validation.
####         :param value any: 
####             The initial value to assign, which will be validated and converted.
####         """
#### 
####         self._name = VariableName
####         self._type = VariableType
####         self._value = self.validate(value)
#### 
####     def __str__(self) -> str:
####         return f"{self._name}:{self._type} = {self._value}"
#### 
####     def validate(self,value:any) -> any:
####         """
####         Validates and converts the value using the variable's type.
#### 
####         Parameters
####         ----------
####         :param value any:
####             The new value to validate
#### 
####         Return
####         ------
####         :return any:
####             The converted value if it's valid.
#### 
####         Raises
####         ------
####             TypeError: If the value cannot be converted to the target type.
####         """
####         try:
####             new_value = self._type(value)
####         except Exception as e:
####             err_msg = f"The value {value} for variable {self._name} isn't converting to the type {self._type}!"
####             raise TypeError(err_msg)
####         
####         # Ajouter logique pour bounds/appartenance
####         return new_value
#### 
####     @staticmethod
####     def constructFromString(line:str) -> 'ConfigVariable':
####         """
####         Parses a configuration line and constructs a ConfigVariable object.
#### 
####         Parameters
####         ----------
####         :param line str: 
####             The configuration string to parse (e.g., 'port:int=8080').
#### 
####         Return
####         ------
####         :return ConfigVariable: 
####             An instance representing the parsed configuration.
#### 
####         Raises
####         ------
####             ValueError: If parsing fails due to incorrect syntax or unsupported type.
####         """
#### 
####         # Extract components
####         components, err_code, err_msg = _extractFromString(line)
#### 
####         # Check for errors:
####         if err_code != "OK":
####             raise ValueError(f"({err_code}) {err_msg}")
####         
####         # Construct variable
####         return ConfigVariable(
####             VariableName = components["name"],
####             VariableType = components["type"],
####             value = components["value"]
####             )
    

