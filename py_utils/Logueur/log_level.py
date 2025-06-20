# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The different log levels
# ---------------------------------------------------------
# ./py_utils/Logueur/log_level.py

"""
Each log message is associated to a severity level, that mirror common logging standards:

+---------+--------+----------------------------------------------------------------------------------------------------------------+
| Name    | number | Description                                                                                                    |
+=========+========+================================================================================================================+
| DEBUG   | 0      | Provides detailed diagnostic information, useful during development or troubleshooting.                        |
+---------+--------+----------------------------------------------------------------------------------------------------------------+
| INFO    | 1      | Conveys general status and operational messages for normal, expected behavior.                                 |
+---------+--------+----------------------------------------------------------------------------------------------------------------+
| WARNING | 2      | Indicates that something unexpected occurred, but the application can continue running.                        |
+---------+--------+----------------------------------------------------------------------------------------------------------------+
| ERROR   | 3      | Represents a significant issue that disrupts part of the system’s functionality.                               |
+---------+--------+----------------------------------------------------------------------------------------------------------------+
| FATAL   | 4      | Denotes a critical error leading to termination of the application (analogous to CRITICAL in many frameworks). |
+---------+--------+----------------------------------------------------------------------------------------------------------------+

These levels are intentionally ordered, with higher numbers signifying more serious conditions, DEBUG being the least critical, and 
FATAL being the most severe. The :class:`LogLevel` class supports comparison operations (`==`, `!=`, `>`, `<`, `>=`, and `<=`), 
allowing easy filtering based on thresholds. Moreover, the :meth:`~LogLevel.factory()` method enables flexible creation of a 
:class:`LogLevel` instance from either a numeric value or a textual name (case-insensitive), e.g., `LogLevel.factory(2)` or 
`LogLevel.factory('warning')` both correspond to the WARNING level.
"""

from enum import Enum
from typing import Union

class LogLevel(Enum):
    """
    Class enumerating the different severity levels supported for a log message. The different levels are defined as in the 
    following:

    - `DEBUG` (0) : Detailed information used for diagnostic.
    - `INFO` (1) : General information for normal operations.
    - `WARNING` (2) : Indication that something unexpected happened, but the application is still running.
    - `ERROR` (3) : Indication that something unexpected happened, but the application is still running.
    - `FATAL` (4) : Critical error causing the termination of the application.

    This class also implement the `==`, `!=`, `>`, `<`, `>=` and `<=` operators for comparing levels, and a factory
    method to create one from either the number or the name.
    """

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

    # self == other
    def __eq__(self, other:Union['LogLevel',int,str]) -> bool:
        """ Equality between 2 LogLevel member """

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)

        return self.value == other.value
    
    # self != other
    def __ne__(self, other:Union['LogLevel',int,str]) -> bool:
        """ Inequality between 2 LogLevel member """

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value != other.value
    
    # self > other
    def __gt__(self, other:Union['LogLevel',int,str]) -> bool:
        """ Greater-than comparison between 2 LogLevel member """

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value > other.value
    
    # self >= other
    def __ge__(self, other:Union['LogLevel',int,str]) -> bool:
        """ Greater-or-equal comparison between 2 LogLevel member """

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value >= other.value
    
    # self < other
    def __lt__(self, other:Union['LogLevel',int,str]) -> bool:
        """ Lower-than comparison between 2 LogLevel member """

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value < other.value
    
    # self <= other
    def __le__(self, other:Union['LogLevel',int,str]) -> bool:
        """ Lower-or-equal comparison between 2 LogLevel member """

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value <= other.value
    

    @classmethod
    def factory(cls, level:Union[str,int]):
        """ 
        Return a member of the LogLevel Enum class for the corresponding level. The level can be the name of
        the level, in upper or lower case, or the number of the level.

        :param level: The wanted level.
        :type level: str or int

        :return: The log level wanted.
        :rtype: LogLevel
        """

        # Type Check:
        # -----------
        if not isinstance(level,(str,int)):
            raise TypeError(f"The level arguments for instanciating an enum member of the LogLevel class must be a str or an int, instead I've received a '{type(level)}'")
        
        # Creating from str:
        # ------------------
        if isinstance(level,str):
            return cls[level.upper()]
        
        # Creating from int:
        # ------------------
        if isinstance(level,int):
            return cls(level)
        
        raise Exception(f"Something unexpected has happened !!")