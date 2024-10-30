# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# The different log levels
# ---------------------------------------------------------
# ./Logueur/log_level.py

""" Module log_level

Implement the LogLevel class, an Enum class for the 
differents levels supported.
"""

from enum import Enum
from typing import Union

class LogLevel(Enum):
    """ LogLevel

    Class enumerating the different levels supported for a
    log message. The different levels are the following:

    - DEBUG   (0) : Detailed information used for diagnostic.
    - INFO    (1) : General information for normal operations.
    - WARNING (2) : Indication that something unexpected happened, 
    but the application is still running.
    - ERROR   (3) : Serious issue that has occurred, causing some
    part of the application to malfunction or fail.
    - FATAL   (4) :  Critical error causing the termination of the
    application.
    """

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

    # self == other
    def __eq__(self, other:Union['LogLevel',int,str]) -> bool:

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)

        return self.value == other.value
    
    # self != other
    def __ne__(self, other:Union['LogLevel',int,str]) -> bool:

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value != other.value
    
    # self > other
    def __gt__(self, other:Union['LogLevel',int,str]) -> bool:

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value > other.value
    
    # self >= other
    def __ge__(self, other:Union['LogLevel',int,str]) -> bool:

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value >= other.value
    
    # self < other
    def __lt__(self, other:Union['LogLevel',int,str]) -> bool:

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value < other.value
    
    # self <= other
    def __le__(self, other:Union['LogLevel',int,str]) -> bool:

        if not isinstance(other,(LogLevel,int,str)):
            return False
        
        if isinstance(other,(int,str)):
            other = LogLevel.factory(other)
        
        return self.value <= other.value
    

    @classmethod
    def factory(cls, level:Union[str,int]):
        """ Factory method

        Return a member of the LogLevel Enum class for the
        corresponding level. The level can be the name of
        the level, in upper or lower case, or the number of
        the level.

        Argument:
        level : Union[str,int]
            The level to get

        Return:
        log_level : LogLevel
            The log level wanted
        """

        # Type Check:
        # -----------
        if not isinstance(level,(str,int)):
            raise ValueError(f"The level arguments for instanciating an enum member of the LogLevel class must be a str or an int, instead I've received a '{type(level)}'")
        
        # Creating from str:
        # ------------------
        if isinstance(level,str):
            return cls[level.upper()]
        
        # Creating from int:
        # ------------------
        if isinstance(level,int):
            return cls(level)
        
        raise Exception(f"Something unexpected has happened !!")