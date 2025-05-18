# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# A log message's topic and a topic filter
# ---------------------------------------------------------
# ./Logueur/logueur.py

""" 
==============
Module logueur
==============

Implement the Logueur class, used for logging messages
to various output, and factury function for this class.
"""

# A way of implementing a singleton, not used
# See https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-a-singleton-in-python
# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]

import datetime
from typing import Union, Optional

from .log_level import LogLevel
from .log_message import LogMessage
from .log_topic import LogTopic, LogTopicFilter
from .log_out import BaseLogHandler, ConsoleLogHandler, FileLogHandler

_default_level = LogLevel.factory("warning")
_default_filter = LogTopicFilter('#')

class Logueur():
    """ 
    =======
    Logueur
    =======

    Object for logging messages to various output. 

    The Logger class allows for managing different outputs for log messages,
    with each output configured differently. This provide a structured
    logging for debugging and monitoring application behavior. It also 
    simplifies the sending of messages by handling the creation of the 
    messages.    
    """

    _default = ConsoleLogHandler(_default_level,_default_filter,supportColor=False,useStderr=True)
    _instance = None

    def __new__(cls,*args,**kwargs):

        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.__init__(*args,**kwargs)
        return cls._instance

    def __init__(self, output:Union[BaseLogHandler,list[BaseLogHandler]],
                 topicGenerationMethode:Optional[str]=None,
                 messageFormat:Optional[str]=None,
                 tz:Optional[datetime.timezone]=None) -> None:
        """ 
        ======================
        Constructor of Logueur
        ======================

        Configure the Logueur with the different output given in argument.

        Parameters
        ----------
        :param output BaseLogHandler|list[BaseLogHandler]:
            The destination of the log's messages. Shall be a class herited
            of the BaseLogHandler or a list of object herited from BaseLogHandler
            in case of mulitple destination.
        :param topicGenerationMethod str|None:
            A string used to determine how to generate the topic of the message.
            Can be 'stack' or 'module', see :mod:`Logueur.log_topic`.
        :param messageFormat str|None:
            A string to be used to format the message before emitting it to the
            differents output. The formatting fubnction used is `str.format` called
            with `level=msg_level` (the level of the log entry), `body=msg_body`
            (the text of the entry), and `topic=msg_topic` (the topic of the entry).
            Note: the `body` must be present in the format !
        """

        # Type Check:
        # -----------

        # Output:
        if not isinstance(output,(BaseLogHandler,list)):
            raise ValueError(f"The output must be BaseLogHandler or a list of BaseLogHandler (or subclass of BaseLogHandler), instead, I've received a '{type(output)}'")
        if not isinstance(output,list):
            output = [output]
        for i,out in enumerate(output,start=1):
            if not isinstance(out,BaseLogHandler):
                raise ValueError(f"Output {i} of the differents outputs must be a BaseLogHandler or a subclass of BaseLogHandler, intead I've received a '{type(out)}'")
        
        # Topic generation method:
        if topicGenerationMethode and not isinstance(topicGenerationMethode,str):
            raise ValueError(f"The topic generation method must be a str, instead I've received a '{type(topicGenerationMethode)}'")
        if topicGenerationMethode and not topicGenerationMethode in LogTopic._fromMethode:
            raise ValueError(f"The topic generation method must be one of the following: {LogTopic._fromMethode}, instead I've received '{topicGenerationMethode}'")
        
        # Log message format:
        if messageFormat and not isinstance(messageFormat,str):
            raise ValueError(f"The message format must be a str, instead I've received a '{type(messageFormat)}'")
        if messageFormat and not r'{body}' in messageFormat:
            raise ValueError("The msg_fmt must at least contains {body} !")
        if tz and not isinstance(tz,datetime.timezone):
            raise TypeError(f"The timezone info (tz) must be a datetime.timezone, instead I've received a '{type(tz)}'")

        # Initialization:
        # ---------------
        self._out = list()
        self._topicGenerationMethode = topicGenerationMethode
        self._messageFormat = messageFormat
        self._timezone = tz

        # Register Output:
        # ----------------
        self.register_output(output)


    def register_output(self, output:Union[BaseLogHandler,list[BaseLogHandler]]) -> None:
        """ 
        =======
        add_out
        =======

        Manually add a log output to the logueur.
        
        Parameters
        ----------
        :param output BaseLogHandler|list[BaseLogHandler]:
            The destination of the log's messages. Shall be a class herited
            of the BaseLogHandler or a list of object herited from BaseLogHandler
            in case of mulitple destination.
        """
        # Type Check:
        # -----------
        if not isinstance(output,(BaseLogHandler,list)):
            raise ValueError(f"The output must be BaseLogHandler or a list of BaseLogHandler (or subclass of BaseLogHandler), instead, I've received a '{type(output)}'")
        if not isinstance(output,list):
            output = [output]
        for i,out in enumerate(output,start=1):
            if not isinstance(out,BaseLogHandler):
                raise ValueError(f"Output {i} of the differents outputs must be a subclass of BaseLogHandler, intead I've received a '{type(out)}'")

        # Add output:
        # -----------
        for out in output:
            self._out.append(out)

    @classmethod
    def log(cls,msg:LogMessage) -> None:
        """ 
        ===
        Log
        ===
        
        Log a specific message. If a instance of Logueur is defined, use its output, else
        use the default one.
        
        Parameters
        ----------
        :param msg LogMessage:
            The message to log
        """
        
        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise ValueError(f"The message to logged must be a LogMessage, instead I've received a '{type(msg)}'")
        
        # Logging:
        # --------
        if cls._instance:
            for out in cls._instance._out:
                out.emit(msg)
        else:
            cls._default.emit(msg)
    
    def debug(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        =====
        debug
        =====

        Log a message with a DEBUG level

        Construct and log a debug message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.

        Parameters
        ----------
        :param body str:
            The text of the message.
        :param topic str|None:
            The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :param format str|None:
            The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`Logueur.log_message.LogMessage`.
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        else:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.DEBUG,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def info(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        ====
        info
        ====

        Log a message with a INFO level

        Construct and log an info message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.

        Parameters
        ----------
        :param body str:
            The text of the message.
        :param topic str|None:
            The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :param format str|None:
            The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`Logueur.log_message.LogMessage`.
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        else:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.INFO,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def warning(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        =======
        warning
        =======
        
        Log a message with a WARNING level

        Construct and log a warning message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.

        Parameters
        ----------
        :param body str:
            The text of the message.
        :param topic str|None:
            The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :param format str|None:
            The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`Logueur.log_message.LogMessage`.
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        else:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.WARNING,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def error(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        =====
        error
        =====
        
        Log a message with a ERROR level

        Construct and log an error message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.

        Parameters
        ----------
        :param body str:
            The text of the message.
        :param topic str|None:
            The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :param format str|None:
            The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`Logueur.log_message.LogMessage`.
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        else:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.ERROR,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def fatal(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        =====
        fatal
        =====
        
        Log a message with a FATAL level

        Construct and log a fatal message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.

        Parameters
        ----------
        :param body str:
            The text of the message.
        :param topic str|None:
            The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :param format str|None:
            The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`Logueur.log_message.LogMessage`.
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        else:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.FATAL,topic,fmt=format,tz=self._timezone)
        self.log(msg)

    @classmethod
    def get_defaultFunc(cls,topic:str,fmt:Optional[str]=None,tz:Optional[datetime.timezone]=None):

        # Type check:
        # -----------
        #TODO
        
        def log(level:Union[str,int],body:str):

            msg = LogMessage(
                body=body,
                level=LogLevel.factory(level),
                topic=LogTopic(topic),
                fmt=fmt,
                tz=tz
            )

            cls.log(msg)

        return log


def ConsoleLogueurFactory(level:Union[str,LogLevel],filter:Union[str,LogTopicFilter]="#",
                          supportColor:bool=True, useStderr:bool=True) -> Logueur:
    """ 
    =====================
    ConsoleLogueurFactory
    =====================
    
    Construct a Logueur configured with an output to the console.
    
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

    Return
    ------
    :return out Logueur:
        The constructed Logueur instance.
    """

    # Type Check:
    # -----------
    if not isinstance(level,(int,str,LogLevel)):
        raise ValueError(f"The level must be a int, a str or a LogLevel, instead I've received a '{type(level)}'")
    if not isinstance(filter,(str,LogTopicFilter)):
        raise ValueError(f"The filter msut be a str or a LogLevel, instead I've received a '{type(filter)}'")
    if not isinstance(supportColor,bool):
        raise ValueError(f"The supportColor argument must be a bool, instead I've received a '{type(supportColor)}'")
    if not isinstance(useStderr,bool):
        raise ValueError(f"The supportColor argument must be a bool, instead I've received a '{type(useStderr)}'")
    
    # Type conversion:
    # ----------------
    if isinstance(level,(str,int)):
        level = LogLevel.factory(level)
    if isinstance(filter,str):
        filter = LogTopicFilter(filter)

    # Create output:
    # --------------
    out = ConsoleLogHandler(level, filter, supportColor, useStderr)
    return Logueur([out])