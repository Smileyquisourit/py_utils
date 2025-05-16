# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Log output
# ---------------------------------------------------------
# ./Logueur/log_out.py

""" 
==============
Module log_out
==============

Implement an abstract base class for defining an output for a logger. This abstract class implement how the messages
are filtered, and define an abstract method that should define how a message is writted.

This module also implement the following log's output:
- ConsoleLogHandler
- FileLogHandler
- RotaryFileLogHandler

Objects
-------

ConsoleLogHandler:
    Represent the interface to write log messages to the console.

FileLogHandler:
    f
"""

#TODO: add a database output

import re
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
    """ 
    =============
    BaseLogOutput
    =============

    Implement the interface that should be provided by a LogOutput class.
    """

    def __init__(self,level:LogLevel,filter:LogTopicFilter) -> None:
        """ Constructor of BaseLogHandler

        An instance of this class represent the interface between the logger
        and the output of the logs.

        Parameters
        ----------
        :param level LogLevel:
            The level used for filtrate log messages.
        :param filter LogTopicFilter:
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

        Parameters
        ----------
        :param msg LogMessage:
            The message to check.

        Return
        ------
        :return bool:
            If the topic is valid or not.
        """

        # Check level:
        # ------------
        if msg.level < self.level:
            return False
        
        # Check topic:
        # ------------
        return self.filter.match(msg.topic)

    def emit(self,msg:LogMessage) -> None:
        """ 
        ====
        emit
        ====
        
        Emit a message to the log.
        
        Filtrate the message given in argument and emit it if it passes the filter and has a 
        correct log level.
        
        Parameters
        ----------
        :param msg LogMessage:
            The message to emit.
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
    """ 
    =================
    ConsoleLogHandler
    =================

    Represent the interface to write log messages to the console.

    An instance of this class can be personalised with two options. The first one is
    to use color when printing the message (if the terminal support it) with the 
    `supportColor` option of the constructor, and if the instance should log the
    `WARNING`, `ERROR`, and `FATAL` standard output of the terminal with the 
    `useStderr` option of the constructor.
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

        Parameters
        ----------
        :param level LogLevel:
            The level used for filtrate log messages.
        :param filter LogTopicFilter:
            The topic filtrer used for filtrate log messages.
        :param supportColor bool:
            If the console support color, and if colors should be used.
            Default to `True`
        :param useStderr bool:
            True to use stderr for warning, error and fatal message.
            Default to `True`
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
        on his critical level

        - DEBUG   -> blue
        - INFO    -> green
        - WARNING -> yellow
        - ERROR   -> red
        - FATAL   -> red

        Parameters
        ----------
        :param msg LogMessage:
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
    """ 
    ==============
    FileLogHandler
    ==============

    Represent the interface to write log messages to a file. The filename of the file in wich to 
    write the log is specified in the constructor, altought a default one can be generated. The
    behavior of the instance when a file with the same name already exist is determined by the 
    `action` option of the constructor.
    """
    _actions = ["overwrite","overwrite-warn","abort","append","new"]

    def __init__(self, level: LogLevel, filter: LogTopicFilter, filename:Optional[str], action:str="abort") -> None:
        """ Constructor of FileLogHandler

        Implement the interface needed to write log messages to a log file.

        It's possible to indicate the filename to use when creating the log file,
        and the `action` argument specify what to do if a file with the same name
        already exist. If no name are specified, a default filename will be used,
        following the ISO 8601 standard: `log_YYYY-MM-DDT:HH:MM:SS`.

        When the 'action' flag is used and a filename with the same name already exist,
        the specified action is taken:
        - 'overwrite'      -> overwrite the file without warning
        - 'overwrite-warn' -> overwrite the file with a warning
        - 'abort'          -> Abort the creation of the handler (default)
        - 'append'         -> Append next log message to the file
        - 'new'            -> Append '(n)' to the filename to create a new file

        Parameters
        ----------
        :param level LogLevel:
            The level used for filtrate log messages.
        :param filter LogTopicFilter:
            The topic filtrer used for filtrate log messages.
        :param filename str|None:
            The name of the log file to create, if no name is supplied, a generic
            name will be generated following ISO 8601 format: log_YYYY-MM-DDT:HH:MM:SS
        :param action str:
            Flag indicating what to do if a file with the same name already exist.
            Default to `abort`.
        """

        # Type Check:
        # -----------
        if filename and not isinstance(filename,str):
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




class LogDirEntry(object):
    """
        A sort of subclass of the DirEntry returned by os.scandir(),
        with a added attribut containing the time of creation determined
        used the file's name.

        Also contain a static method for reconstructing a time (an instance 
        of datetime.datetime) determined using the file's name and a pattern.

        All the methods/attributes of DirEntry are accesible by using the
        __getattribute__ of the DirEntry in this class __getattr__.
    """

    def __init__(self,dirEntry, creationTime:datetime.datetime):

        # Type check:
        if not isinstance(creationTime,datetime.datetime):
            raise TypeError(f"The creation time should be a 'datetime.datetime' object, instead I've received a {type(creationTime)}")
        self._dirEntry = dirEntry
        self.creationTime = creationTime

    def __getattr__(self, name):
        return self._dirEntry.__getattribute__(name)
    
    def __repr__(self):
        return f"<LogDirEntry '{self.name}'>"
    
    def __str__(self):
        return self.__repr__()

class RotaryFileLogHandler(BaseLogHandler):

    _ISO_FMT_STR_PATTERN = \
        r"{base}(?P<date>\d{{4}}-\d{{2}}-\d{{2}}){timeSep}(?P<time>\d{{2}}:\d{{2}}:\d{{2}})" + \
        r"(?>\.(?P<time_ms>\d{{6}}))?(?P<tz>[+-]\d{{2}}:\d{{2}})?{ext}"
    
    _LOG_FILE_FMT = "{base}{{date}}{timeSep}{{time}}{ext}"
    
    _SUPPORTED_LOG_UNIT = ('file','day','week','month')

    @property
    def logfiles(self) -> tuple[LogDirEntry]:
        """ 
            A tuple of LogDirEntry obtained with `os.scandir`.

            An attribute `creationTime` is added wich represent the creation time
            of the file using it's name.
        """
        _logFiles =  tuple(entry for entry in os.scandir(self._directory) if self._filename_pattern.fullmatch(entry.name))
        _creationTimes = tuple(self._reconstruct_time_from_filename(file.name) for file in _logFiles)
        return tuple(LogDirEntry(file,createdTime) for file, createdTime in zip(_logFiles,_creationTimes))


    def __init__(self, level: LogLevel, filter: LogTopicFilter, baseFilename:str="log_", directory:str='.',
                 log_ext: str = '', timeSep:str='T', tz:datetime.timezone=datetime.timezone.utc,
                 maxSizeFile:int=10*1024**2, maxLog:int=5, maxLogUnit:str='file'):
        
        # Type/Value Check:
        # -----------------
        if not isinstance(baseFilename,str):
            raise TypeError(f"The filename must be a str, instead I've received a '{type(baseFilename)}'")
        if not isinstance(log_ext,str):
            raise TypeError(f"The filename extension (log_ext) must be a str, instead I've received a '{type(log_ext)}'")
        if not isinstance(directory,str):
            raise TypeError(f"The directory must be a str, instead I've received a '{type(directory)}'")
        if not isinstance(timeSep,str):
            raise TypeError(f"The time / date separator (timeSep) must be a str, instead I've received a '{type(timeSep)}'")
        if not isinstance(tz,datetime.timezone):
            raise TypeError(f"The timezone (tz) must be a 'datetime.timezone', instead I've received a '{type(tz)}'")
        if not isinstance(maxSizeFile,int):
            raise TypeError(f"The maximum size of file (maxSizeFile) must be a int, instead I've received a '{type(maxSizeFile)}'")
        if not isinstance(maxLog,int):
            raise TypeError(f"The maximum number of file (maxLog) must be a int, instead I've received a '{type(maxLog)}'")
        if not isinstance(maxLogUnit,str):
            raise TypeError(f"The unit of maximum number of file (maxLogUnit) must be a str, instead I've received a '{type(maxLog)}'")
        if not maxLogUnit in self._SUPPORTED_LOG_UNIT:
            raise ValueError(f"Unsupported option {maxLogUnit}, it should be in {self._SUPPORTED_LOG_UNIT}")
        
        # Check directory
        absPath_dir = os.path.abspath(directory)
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"The directory {absPath_dir} wasn't found!")

        # Initialize instance:
        # --------------------
        super().__init__(level, filter)
        self._directory = absPath_dir
        self._filename_fmt = self._LOG_FILE_FMT.format(base=baseFilename,timeSep=timeSep,ext=log_ext)
        self._filename_pattern = re.compile(self._ISO_FMT_STR_PATTERN.format(base=baseFilename,timeSep=timeSep,ext=log_ext))
        self._current_file = None

        self._tz = tz

        self._maxSize = maxSizeFile
        self._maxLog = maxLog
        self._maxLogUnit = maxLogUnit


    # Dunder methods:
    # ---------------

    def __len__(self) -> int:
        return len(self.logfiles)


    # Methods for creating/cleaning filelog:
    # --------------------------------------

    def _clean_num(self,tmp_rec=0):
        """ Check all known logfile from number and remove the oldest one if their is too many. """
        _logFiles = self.logfiles
        if len(_logFiles) > self._maxLog:
            oldest_file = None
            oldest_time = datetime.datetime.now(self._tz)
            for logfile in _logFiles:
                if logfile.creationTime < oldest_time:
                    oldest_file = logfile.name
                    oldest_time = logfile.creationTime
            
            if not oldest_file:
                raise Exception(f"The oldest logfile found is in the future!! The logfile name: {oldest_file}")
            
            file_to_remove = os.path.join(self._directory,oldest_file)
            os.remove( os.path.abspath(file_to_remove) )

        # Recursive calls until their is no more than self._maxLog files,
        # That should never happen, but it's their just in case.
        if len(self.logfiles) > self._maxLog:
            warnings.warn("At one point, log's files weren't correctly cleaned (logFile by number) !!")
            self._clean_num(tmp_rec=tmp_rec+1)

    def _clean_date(self):
        """ Check all known logfile from date """

        # Compute max_timedelta
        if self._maxLogUnit == 'day':
            max_timedelta = datetime.timedelta(days=self._maxLog)
        elif self._maxLogUnit == 'week':
            max_timedelta = datetime.timedelta(weeks=self._maxLog)
        elif self._maxLogUnit == 'month':
            max_timedelta = datetime.timedelta(weeks=self._maxLog*4)
        else:
            raise ValueError(f"Unrecognized _maxLogUnit '{self._maxLogUnit}' when cleaning logfiles by date!")
        
        # Remove old logfiles
        now = datetime.datetime.now(self._tz)
        for file in self.logfiles:
            dt = now - file.creationTime
            if dt > max_timedelta:
                os.remove( os.path.abspath(file.name) )
            if dt < datetime.timedelta(0):
                raise Exception(f"One logfile is in the future!! The logfile name: {file.name}")

    def _request_new_logfile(self):
        """ Create a new log file and then call right method for cleaning logfile """

        # Create new file
        now = datetime.datetime.now(self._tz)
        filename_components = {
            "date": now.date().isoformat(),
            "time": now.timetz().isoformat()
        }
        new_filename = self._filename_fmt.format(**filename_components)
        new_file = os.path.join(self._directory,new_filename)
        try:
            with open(new_file,'x') as f:
                os.fsync(f.fileno())
        except Exception as e:
            raise Exception(f"Error while requesting a new logfile: {e}")
        

        # Clean logfiles
        if self._maxLogUnit == "file":
            self._clean_num()
        else:
            self._clean_date()

        return new_file


    # Private methods:
    # ----------------

    def _reconstruct_time_from_filename(self,filename:str):
        if re_match := self._filename_pattern.match(filename):
            
            # Extract components
            date = re_match.group('date')
            time = re_match.group('time')
            ms = re_match.group('time_ms')
            tz = re_match.group('tz')

            # Reconstruct datetime.datetime
            reconstructed_datetime_str = f"{date}T{time}{'.'+str(ms) if ms else ''}{tz if tz else ''}"
            return datetime.datetime.fromisoformat(reconstructed_datetime_str)
        else:
            raise ValueError(f"The format of filename '{filename}' is invalid!")

    def _write(self, msg:LogMessage):
        """ Write a message to the current logfile.

        If their no current_file (ie for the first message to be logged) or if it's
        size is greater than the max authorized, create a new file and clean-up logfiles
        according to user will, then write the message.
        """

        if not self._current_file or os.path.getsize( self._current_file ) > self._maxSize:
            self._current_file = self._request_new_logfile()

        with open(self._current_file,'a') as f:
            f.write( str(msg) )
            os.fsync(f.fileno())