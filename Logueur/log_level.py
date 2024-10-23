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
    def __eq__(self, other:'LogLevel') -> bool:
        if not isinstance(other,LogLevel):
            return False
        return self.value == other.value
    
    # self != other
    def __ne__(self, other:'LogLevel') -> bool:
        if not isinstance(other,LogLevel):
            return False
        return self.value != other.value
    
    # self > other
    def __gt__(self, other:'LogLevel') -> bool:
        if not isinstance(other,LogLevel):
            return False
        return self.value > other.value
    
    # self >= other
    def __ge__(self, other:'LogLevel') -> bool:
        if not isinstance(other,LogLevel):
            return False
        return self.value >= other.value
    
    # self < other
    def __lt__(self, other:'LogLevel') -> bool:
        if not isinstance(other,LogLevel):
            return False
        return self.value < other.value
    
    # self <= other
    def __le__(self, other:'LogLevel') -> bool:
        if not isinstance(other,LogLevel):
            return False
        return self.value <= other.value