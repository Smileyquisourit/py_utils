# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Log output
# ---------------------------------------------------------
# ./Logueur/log_out.py

""" Module log_out

Implement an abstract base class for defining an output
for a logger. This abstract class implement how the messages
are filtered, and define an abstract method that should define
how a message is writted.
"""

import os
import sys
import warnings
import datetime
from typing import Optional
from abc import ABC, abstractmethod

from .log_level import LogLevel
from .log_topic import LogTopicFilter
from .log_message import LogMessage


class BaseLogHandler(ABC):
    """ BaseLogOutput

    Implement the interface that should be provided
    by a LogOutput class.
    """

    def __init__(self,level:LogLevel,filter:LogTopicFilter) -> None:
        """ Constructor of BaseLogHandler

        An instance of this class represent the interface between the logger
        and the output of the logs.

        Arguments:
        level : LogLevel
            The level used for filtrate log messages.
        filter : LogTopicFilter
            The topic filtrer used for filtrate log messages.
        """

        # Type Check:
        # -----------
        if not isinstance(level,LogLevel):
            raise ValueError(f"The level must be a LogLevel, instead I've received a '{type(level)}'")
        if not isinstance(filter,LogTopicFilter):
            raise ValueError(f"The topic filter must be a LogTopicFilter, instead I've received a '{type(level)}'")


        # Initialization:
        # ---------------
        super().__init__()
        self.level = level
        self.filter = filter

        # Change doc-string:
        # ------------------
        # Change the docstring of the emit methode by the one of the _write
        # methode, if there is one.
        #if self._write.__doc__:
        #    self.emit.__doc__ = self._write.__doc__

    @abstractmethod
    def _write(self,msg:LogMessage) -> None:
        """ 
        Abstract method that should implement how the message is emitted. 
        """
        pass

    def _filtrate(self,msg:LogMessage) -> bool:
        """ Check if a message should be emited.

        Check if the level of the message is more critical
        than the level registered, and if the topic match.
        """

        # Check level:
        # ------------
        if msg.level < self.level:
            return False
        
        # Check topic:
        # ------------
        return self.filter.match(msg.topic)

    def emit(self,msg:LogMessage) -> None:
        """ Emit a message to the log
        
        Filtrate the message given in argument and emit it
        if it passes the filter and has a correct log level.
        
        """

        # Change the docstring of the emit methode by the one of the _write
        # methode, if there is one.
        if self._write.__doc__:
            __doc__ = self._write.__doc__

        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise ValueError(f"The message to emit must be a LogMessage, instead I've received a '{type(msg)}'")
        
        # Emit the message:
        # -----------------
        if self._filtrate(msg):
            self._write(msg)


class ConsoleLogHandler(BaseLogHandler):
    """ ConsoleLogHandler

    Represent the interface to write log messages to the console.
    """

    _FG_COLORS = {
        "DEBUG" : '\033[34m',
        "INFO" : '\033[92m',
        "WARNING" : '\033[93m',
        "ERROR" : '\033[91m',
        "FATAL" : '\033[91m'
    }
    _FG_RS = '\033[0m'

    def __init__(self,level:LogLevel,filter:LogTopicFilter,
                 supportColor:bool=True, useStderr:bool=True) -> None:
        """ Constructor of ConsoleLogHandler

        Initialize an instance of the class, that is responsible to
        print log message to the console.

        Arguments:
        level : LogLevel
            The level used for filtrate log messages.
        filter : LogTopicFilter
            The topic filtrer used for filtrate log messages.
        supportColor : bool = True
            If the console support color, and if colors should be used.
        useStderr : bool = True
            True to use stderr for warning, error and fatal message.
        """

        # Type Check:
        # -----------
        if not isinstance(supportColor,bool):
            raise ValueError(f"The supportColors argument must be a bool, instead I've received a '{type(supportColor)}'")
        if not isinstance(useStderr,bool):
            raise ValueError(f"The useStderr argument must be a bool, instead I've received a '{type(useStderr)}'")

        # Initialization:
        # ---------------
        super().__init__(level,filter)
        self._supportColor = supportColor
        self._useStderr = useStderr

    def _write(self,msg:LogMessage) -> None:
        """ Emit a log message to the console.

        Print the log message to the console. If the colors are
        supported, a color will be applied to the message depending
        on his critical level:
        - DEBUG   -> blue
        - INFO    -> green
        - WARNING -> yellow
        - ERROR   -> red
        - FATAL   -> red

        Argument:
        msg : LogMessage
            The log message to emit.
        """

        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise ValueError(f"The message to emit must be a LogMessage, instead I've received a '{type(msg)}'")
        
        # Color the message:
        # ------------------
        if self._supportColor:
            msg_str = f"{self._FG_COLORS[msg.level.name]}{msg}{self._FG_RS}"
            #msg.body = self._FG_COLORS[msg.level.name] + msg.body + self._FG_RS
        else:
            msg_str = str(msg)

        # Emit the message:
        # -----------------
        if self._useStderr and msg.level >= LogLevel.WARNING:
            out = sys.stderr
        else:
            out = sys.stdout
        out.write(msg_str)
        out.flush()

class FileLogHandler(BaseLogHandler):
    """ FileLogHandler

    Represent the interface to write log messages to a file.
    """
    _actions = ["overwrite","overwrite-warn","abort","append","new"]

    def __init__(self, level: LogLevel, filter: LogTopicFilter, filename:Optional[str], action:str="abort") -> None:
        """ Constructor of FileLogHandler

        Implement the interface needed to write log messages to a log file.

        It's possible to indicate the filename to use when creating the log file,
        and the 'append' argument specify what to do if a file with the same name
        already exist. If no name are specified, a default filename will be used,
        following the ISO 8601 standard: 'log_YYYY-MM-DDT:HH:MM:SS'.

        If the 'action' flag is used when a filename with the same name already exist,
        and specified witch action to take:
        - 'overwrite'      -> overwrite the file without warning
        - 'overwrite-warn' -> overwrite the file with a warning
        - 'abort'          -> Abort the creation of the handler (default)
        - 'append'         -> Append next log message to the file
        - 'new'            -> Append '(n)' to the filename to create a new file

        Arguments
        level : LogLevel
            The level used for filtrate log messages.
        filter : LogTopicFilter
            The topic filtrer used for filtrate log messages.
        filename : Optional[str]
            The name of the log file to create, if no name is supplied, a generic
            name will be generated following ISO 8601 format: log_YYYY-MM-DDT:HH:MM:SS
        action : str = abort
            Flag indicating what to do if a file with the same name already exist
        """

        # Type Check:
        # -----------
        if not filename and not isinstance(filename,str):
            raise ValueError(f"The filename must be a str, instead I've received a '{type(filename)}'")
        if not isinstance(action,str):
            raise ValueError(f"The action argument must be a str, instead I've received a '{type(action)}'")
        if not action in self._actions:
            raise ValueError(f"The action argument must be in {self._actions}, instead I've received '{action}'")
        
        # Initialize instance:
        # --------------------
        super().__init__(level, filter)
        if not filename:
            filename = self._generateLogFilename()

        # check filename :
        if action == 'overwrite':
            with open(filename,'w'): pass
            self._filename = filename

        elif action == 'overwrite-warn':
            if os.path.isfile(filename):
                warnings.warn(f"The file {filename} already exist, it's contents will be erased !",ResourceWarning)
            with open(filename,'w'): pass
            self._filename = filename
        
        elif action == 'abort':
            if os.path.isfile(filename):
                raise FileExistsError(f"The log file {filename} already exist !")
            
        else: # action == 'new'
            self._filename = self._makeValideFilename(filename)
            with open(filename,'w'): pass
    
    def _write(self, msg:LogMessage) -> None:
        """ Append a message to the end of the log file.
        """

        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise ValueError(f"The message to emit must be a LogMessage, instead I've received a '{type(msg)}'")
        
        # Emit the message:
        # -----------------
        with open(self._filename,'a') as f:
            f.write(msg)
    
    @staticmethod
    def _generateLogFilename() -> str:
        """ generate a log filename with ISO 8601 format """
        now = datetime.datetime.now(datetime.timezone.utc)
        return "log_"+now.isoformat()
    @staticmethod
    def _makeValideFilename(filename:str) -> str:
        """ Make a valide filename

        Take a filename and check if it's valide. If it's not,
        the string '_(n)' will be appended to the file name, with
        n a integer. This integer will start at 1, and will be
        incremented by one the necessary number of time for the
        filename to be unique.
        """
        base, ext = os.path.splitext(filename)
        i = 1
        while os.path.exists(filename):
            filename = f"{base}_{i}{ext}"
            i += 1
        return filename