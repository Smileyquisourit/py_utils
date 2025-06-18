# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Log output
# ---------------------------------------------------------
# ./py_utils/Logueur/log_out.py

"""

**Text from Logueur/log_out.py**

Implement an abstract base class for defining an output for a logger. This abstract class implement how the messages
are filtered, and define an abstract method that should define how a message is writted.

This module also implement the following log's output:
- ConsoleLogHandler
- FileLogHandler
- RotaryFileLogHandler

Classes
-------

BaseLogHandler(ABC):
    An abstract base class describing the interface for creating a log handler. It also implement some functionalities
    that should be shared by all loh handler.

ConsoleLogHandler(BaseLogHandler):
    Implement the interface to write log messages to the standard output (generaly the console). It contains differents
    options for coloring the message and use the standart error output for `ERROR` and `FATAL` message instead of the standard
    output.

FileLogHandler(BaseLogHandler):
    Implement the interface for writing log messages to a file.

RotaryFileLogHandler(BaseLogHandler):
    Implement the interface for writing log messages to a file, while changing file if the previous one's size exceed a fixed
    amount, and deleting oldest file on some conditions.
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

# Base class
# ----------

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
        :param level: The level used to filtrate log messages.
        :type level: LogLevel

        :param filter: The topic filter used to filtrate log messages.
        :type filter: LogTopicFilter
        """

        # Type Check:
        # -----------
        if not isinstance(level,LogLevel):
            raise TypeError(f"The level must be a LogLevel, instead I've received a '{type(level)}'")
        if not isinstance(filter,LogTopicFilter):
            raise TypeError(f"The topic filter must be a LogTopicFilter, instead I've received a '{type(filter)}'")


        # Initialization:
        # ---------------
        super().__init__()
        self.level = level
        self.filter = filter

    @abstractmethod
    def _write(self,msg:LogMessage) -> None:
        """ 
        Abstract method that should implement how the message is emitted.

        Parameters
        ----------
        :param msg: The message to write.
        :type msg: LogMessage
        """
        pass

    def _filtrate(self,msg:LogMessage) -> bool:
        """ Check if a message should be emited.

        Check if the level of the message is more critical than the level registered, and if the 
        topic match.

        Parameters
        ----------
        :param msg: The message to check.
        :type msg: LogMessage

        Return
        ------
        :return: If the topic is valid or not.
        :rtype: bool
        """

        # Check level:
        # ------------
        if msg.level < self.level:
            return False
        
        # Check topic:
        # ------------
        return self.filter.match(msg.topic)

    def emit(self,msg:LogMessage) -> None:
        """ Emit a message to the log.
        
        Filtrate the message given in argument and emit it if it passes the filter and has a 
        correct log level.
        
        Parameters
        ----------
        :param msg: The message to emit.
        :type msg: LogMessage
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


# Helper Class:
# -------------

class LogDirEntry(object):
    """
    ===========
    LogDirEntry
    ===========
    
    A sort of subclass of the DirEntry returned by os.scandir(), with an added attribut containing the time 
    of creation determined using the file's name or other means.

    All the methods/attributes of DirEntry are accesible by using the __getattribute__ of the DirEntry with 
    this class __getattr__.
    """

    creationTime: datetime.datetime

    def __init__(self,dirEntry:os.DirEntry, creationTime:datetime.datetime):
        """ Constructor of LogDirEntry.

        A sort of subclass of the DirEntry returned by os.scandir(), with an added attribut containing the time 
        of creation determined using the file's name or other means.

        Parameters
        ----------
        :param dirEntry: The DirEntry object that should be sort of subclassed
        :type dirEntry: os.DirEntry

        :param creationTime: The datetime creation time of the file of the associated DirEntry.
        :type creationTime: datetime.datetime
        """

        # Type check:
        # -----------
        if not isinstance(dirEntry,os.DirEntry):
            raise TypeError(f"The dirEntry should be a 'os.DirEntry' object, instead I've received a {type(dirEntry)}")
        if not isinstance(creationTime,datetime.datetime):
            raise TypeError(f"The creation time should be a 'datetime.datetime' object, instead I've received a {type(creationTime)}")
        
        # Initialise intance:
        # -------------------
        self._dirEntry = dirEntry
        self.creationTime = creationTime

    def __getattr__(self, name) -> any:
        return self._dirEntry.__getattribute__(name)
    
    def __repr__(self) -> str:
        return f"<LogDirEntry '{self.name}'>"
    
    def __str__(self) -> str:
        return self.__repr__()


# Log handlers:
# -------------

class ConsoleLogHandler(BaseLogHandler):
    """ 
    =================
    ConsoleLogHandler
    =================

    Represent the interface to write log messages to the console.

    An instance of this class can be personalised with two options. The first one is to use color
    when printing the message (if the terminal support it) with the `supportColor` option of the 
    constructor, and if the instance should log the `WARNING`, `ERROR`, and `FATAL` standard output 
    of the terminal with the `useStderr` option of the constructor.
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
        :param level: The level used for filtrate log messages.
        :type level: LogLevel

        :param filter: The topic filtrer used for filtrate log messages.
        :type filter: LogTopicFilter

        :param supportColor: If the console support color, and if colors should be used.
            Default to `True`
        :type supportColor: bool

        :param useStderr bool: True to use stderr for warning, error and fatal message.
            Default to `True`
        :type useStderr: bool
        """

        # Base initialisation and type check:
        # -----------------------------------
        super().__init__(level,filter)

        # Type Check:
        # -----------
        if not isinstance(supportColor,bool):
            raise ValueError(f"The supportColors argument must be a bool, instead I've received a '{type(supportColor)}'")
        if not isinstance(useStderr,bool):
            raise ValueError(f"The useStderr argument must be a bool, instead I've received a '{type(useStderr)}'")

        # Initialization:
        # ---------------
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
        :param msg: The log message to emit.
        :type msg: LogMessage
        """

        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise TypeError(f"The message to emit must be a LogMessage, instead I've received a '{type(msg)}'")
        
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
        - 'append'         -> Append next log message to the file, creating it if it doesn't exist
        - 'new'            -> Append '(n)' to the filename to create a new file

        Parameters
        ----------
        :param level: The level used for filtrate log messages.
        :type level: LogLevel

        :param filter : The topic filtrer used for filtrate log messages.
        :type filter: LogTopicFilter

        :param filename: The name of the log file to create, if no name is supplied, a generic
            name will be generated following ISO 8601 time format: log_YYYY-MM-DDT:HH:MM:SS[+-]HH:MM
            using UTC as timezone.
        :type filename: str or None

        :param action: Flag indicating what to do if a file with the same name already exist. Can be
            `'overwrite'`, `'overwrite-warn'`, `'abort'`, `'append'`, or `'new'`
            Default to `abort`.
        :type action: str
        """

        # Base initialisation and type check:
        # -----------------------------------
        super().__init__(level, filter)

        # Type Check:
        # -----------
        if filename and not isinstance(filename,str):
            raise TypeError(f"The filename must be a str, instead I've received a '{type(filename)}'")
        if not isinstance(action,str):
            raise TypeError(f"The action argument must be a str, instead I've received a '{type(action)}'")
        if not action in self._actions:
            raise ValueError(f"The action argument must be in {self._actions}, instead I've received '{action}'")
        
        # Initialize instance:
        # --------------------
        if not filename:
            filename = self._generateLogFilename()

        # check filename :
        if action == 'overwrite':
            with open(filename,'w'): pass

        elif action == 'overwrite-warn':
            if os.path.isfile(filename):
                warnings.warn(f"The file {filename} already exist, it's contents will be erased !",ResourceWarning)
            with open(filename,'w'): pass
        
        elif action == 'abort':
            if os.path.isfile(filename):
                raise FileExistsError(f"The log file {filename} already exist !")
            
        elif action == 'append':
            pass
            
        else: # action == 'new'
            filename = self._makeValideFilename(filename)
            with open(filename,'w'): pass
        
        self._filename = filename
    
    def _write(self, msg:LogMessage) -> None:
        """ Append a message to the end of the log file.

        Parameters
        ----------
        :param msg: The message to write.
        :type msg: LogMessage
        """

        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise TypeError(f"The message to emit must be a LogMessage, instead I've received a '{type(msg)}'")
        
        # Emit the message:
        # -----------------
        with open(self._filename,'a') as f:
            f.write( str(msg) )
            #os.fsync(f.fileno())
    
    @staticmethod
    def _generateLogFilename() -> str:
        """ generate a log filename with ISO 8601 format using UTC timezone 
        
        Returns
        -------
        :return: The datetime in ISO 8601 format, using UTC timezone, prepended by `'log_'`
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        return "log_"+now.isoformat()
    @staticmethod
    def _makeValideFilename(filename:str) -> str:
        """ Make a valide filename

        Take a filename and check if it's valide. If it's not, the string `'_(n)'` will be appended to 
        the file name, with `n` a integer. This integer will start at 1, and will be incremented by one 
        the necessary number of time for the filename to be unique.

        This methods doesn't create the file!!

        Parameters
        ----------
        :param filename: The filename to check
        :type filename: str

        Return
        ------
        :return: A filename valid
        :rtype: str
        """
        base, ext = os.path.splitext(filename)
        i = 1
        while os.path.exists(filename):
            filename = f"{base}_{i}{ext}"
            i += 1
        return filename

class RotaryFileLogHandler(BaseLogHandler):
    """ 
    ====================
    RotaryFileLogHandler
    ====================

    Represent the interface to write log messages to a set of logfile. A new logfile is generated
    when the previous one's size exceed a certain size, determined by the user, and only a fixed
    amount of logfile is keep (determined by the user).
    """

    _ISO_FMT_STR_PATTERN = \
        r"{base}(?P<date>\d{{4}}-\d{{2}}-\d{{2}}){timeSep}(?P<time>\d{{2}}:\d{{2}}:\d{{2}})" + \
        r"(?>\.(?P<time_ms>\d{{6}}))?(?P<tz>[+-]\d{{2}}:\d{{2}})?{ext}"
    
    _LOG_FILE_FMT = "{base}{{date}}{timeSep}{{time}}{ext}"
    
    _SUPPORTED_LOG_UNIT = ('file','day','week','month')

    @property
    def logfiles(self) -> tuple[LogDirEntry]:
        """ 
            A tuple of LogDirEntry obtained with a DirEntry obtained by `os.scandir`, and
            the creation time obtained from it's name.
        """

        # Get dirEntry and datetime
        _logFiles =  tuple(entry for entry in os.scandir(self._directory) if self._filename_pattern.fullmatch(entry.name))
        _creationTimes = tuple(self._reconstruct_time_from_filename(file.name) for file in _logFiles)

        # Sort datetime indices
        _sorted_idx = [i for i, _ in sorted(enumerate(_creationTimes), key=lambda x: x[1])]
        return tuple(
            LogDirEntry(_logFiles[i],_creationTimes[i]) for i in _sorted_idx
        )


    def __init__(self, level: LogLevel, filter: LogTopicFilter, baseFilename:str="log_", directory:str='.',
                 log_ext: str = '', timeSep:str='T', tz:datetime.timezone=datetime.timezone.utc,
                 maxSizeFile:int=10*1024**2, maxLog:int=5, maxLogUnit:str='file'):
        """ Constructor of RotaryFileLogHandler.

        An instance of RotaryFileLogHandler is an interface to write log messages to a set of files. A new 
        file is created when the previous one's size exceed the limit specified by `maxSizeFile`. The log's
        files aren't all conserved, and at some point old files are deleted. This behavior is controlled with
        the two arguments `maxLog` and `maxLogUnit`, where `maxLog` is a `int` and it is interpreted in different
        ways depending on the value of `maxLogUnit`:
        - if `maxLogUnit='file'` : only the `maxLog` latest files are keep.
        - if `maxLogUnit='day'` : only files no older than `maxLog` days are conserved.
        - if `maxLogUnit='week'` : only files no older than `maxLog` weeks are conserved.
        - if `maxLogUnit='month'` : only files no older than `maxLog` months are conserved.

        This file clean-up only occurs when a new logfile is requested (du to the size limit), so if you allow a
        large size for a log file, there is no garanty that file older than what you requested are deleted at any time.

        # TODO
        A new logfile is only requested when their is the need to write a message, so if your application never need to
        write a message, there will be no logfiles ! This behavior will maybe be customizable in the future.

        Parameters
        ----------
        :param level: The level used for filtrate log messages.
        :type level: LogLevel

        :param filter: The topic filtrer used for filtrate log messages.
        :type filter: LogTopicFilter

        :param baseFilename: The base used to construct the log's filenames. The datetime using ISO 8601 format
            will be append to this base. Default is `'log_'`
        :type baseFilename: str, optional

        :param directory: The directory in wich to save the logs file. As for now, this directory will not be created !
            Default is the current directory.
        :type directory: str, optional

        :param log_ext: The extension of the log's filenames. Default is no extention `''`
        :type log_ext: str, optional

        :param timeSep: The separator to use between the date and the time in the ISO 8601 format for datetime. Default
            is `'T'`
        :type timeSep: str, optional

        :param tz: The time zone to use when generating datetime for the log's filenames. Default is UTC.
        :type tz: datetime.timezone, optional

        :param maxFileSize: The maximum size of a log file before requesting a new file, in byte. Default is 10MB
        :type maxFileSize: int, optional

        :param maxLog: A positive integer that defines the retention threshold. The way this integer is interpreted
            depends on the `maxLogUnit` argument. Default to 5.
        :type maxLog: int, optional

        :param maxLogUnit: An indicator of how the `maxLog` value should be interpreted. If `'file'`, it's interpreted
            as the maximum number of log files to keep, if time based (`'day'`,`'week'`, or `'month'`), it's interpreted
            as the maximum age of a log file. Default to `'file'`
        :type maxLogUnit: str, optional
        """

        # Base initialisation and type check:
        # -----------------------------------
        super().__init__(level, filter)
        
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
        absPath_dir = self._check_dir(directory)
        
        # Check maxLog:
        if maxLog <= 0:
            raise ValueError(f"The 'maxLog' should be stricly positiv (> 0), but I've received {maxLog}")

        # Initialize instance:
        # --------------------
        self._directory = absPath_dir
        self._filename_fmt = self._LOG_FILE_FMT.format(base=baseFilename,timeSep=timeSep,ext=log_ext)
        self._filename_pattern = re.compile(self._ISO_FMT_STR_PATTERN.format(base=baseFilename,timeSep=timeSep,ext=log_ext))

        self._tz = tz

        self._maxSize = maxSizeFile
        self._maxLog = maxLog
        self._maxLogUnit = maxLogUnit

        self._current_file = self._init_logfiles()


    # Dunder methods:
    # ---------------

    def __len__(self) -> int:
        return len(self.logfiles)


    # Methods for creating/cleaning filelog:
    # --------------------------------------

    def _clean_num(self) -> None:
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
        # That should never happen, but it's there just in case.
        if len(self.logfiles) > self._maxLog:
            warnings.warn("At one point, log's files weren't correctly cleaned (maxLogUnit is 'file') !!")
            self._clean_num()

    def _clean_date(self) -> None:
        """ Check all known logfile from datetime. """

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
                os.remove( os.path.abspath(file.path) )
            if dt < datetime.timedelta(0):
                raise Exception(f"One logfile is in the future!! The logfile name: {file.name}")

    def _clean_logfiles(self) -> None:
        """ Call the right method for cleaning the logfiles. """

        if self._maxLogUnit == "file":
            self._clean_num()
        else:
            self._clean_date()

    def _request_new_logfile(self) -> str:
        """ Create a new log file and then call right method for cleaning logfile. 
        
        Return
        ------
        :return: The name of the new logfile created.
        :rtype: str
        """

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

        return new_file
    
    def _init_logfiles(self):
        """ Intialise the logfiles system. """

        # Clean logfiles
        self._clean_logfiles()
        _logfiles = self.logfiles
        
        # Case where there is no logfiles
        if len(_logfiles) == 0:
            return None
        
        return _logfiles[-1].path
        


    # Private methods:
    # ----------------

    def _reconstruct_time_from_filename(self,filename:str) -> datetime.datetime:
        """ Compute the datetime of the creation of a logfile, using it's name.

        Parameters 
        ----------
        :param filename: The filename of the file for wich the datetime creation is requested.
        :type filename: str

        Return
        ------
        :return: The datetime.datetime object corresponding to the creation of the file.
        :rtype: datetime.datetime

        Raise
        -----
        :raises ValueError: When the format of the filename isn't recognized.
        """
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

    def _check_dir(self,dirname:str) -> str:
        """ Check if the directory exist, creating if necessary.

        This method check if the parent directory exist (will raise an error if not),
        then check if the directory exist and create it if necessary.

        Parameters
        ----------
        :param dir_path: The name of the directory wanted by the user.
        :type dir_path: str

        Return
        ------
        :return: the full path to the directory wanted by the user.
        :rtype: str

        Raises
        ------
        :raise FileNotFoundError: when the parent directory isn't found.
        """

        # Get absolute path
        abs_path = os.path.abspath(dirname)
        
        # Check parent directory
        parent = os.path.dirname(abs_path)
        if not os.path.isdir(parent):
            raise FileNotFoundError(f"The parent directory '{parent}' of the requested directory for the logfiles wasn't found !")
        
        # Check requested directory:
        if not os.path.isdir(abs_path):
            os.mkdir(abs_path)
        
        return abs_path

    def _write(self, msg:LogMessage) -> None:
        """ Write a message to the current logfile.

        If their no current_file (ie for the first message to be logged when there is no exisiting
        logfiles) or if it's size is greater than the max authorized, create a new file and clean-up 
        logfiles according to user will, then write the message.

        Parameter
        ---------
        :param msg: The log message to write to the file.
        :type msg: LogMessage
        """

        if not self._current_file or os.path.getsize( self._current_file ) > self._maxSize:
            self._clean_logfiles()
            self._current_file = self._request_new_logfile()

        with open(self._current_file,'a') as f:
            f.write( str(msg) )
            os.fsync(f.fileno())
