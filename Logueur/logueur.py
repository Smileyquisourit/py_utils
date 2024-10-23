# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# A log message's topic and a topic filter
# ---------------------------------------------------------
# ./Logueur/logueur.py

""" Module logueur

Implement the Logueur class, used for logging messages
to various output.
"""

from typing import Union, Optional

from .log_level import LogLevel
from .log_message import LogMessage
from .log_topic import LogTopic, LogTopicFilter
from .log_out import BaseLogHandler, ConsoleLogHandler, FileLogHandler

class Logueur():
    """ Logueur

    Object for logging messages to various output. 

    The Logger class allows for managing different outputs for log messages,
    with each output configured differently. This provide a structured
    logging for debugging and monitoring application behavior. It also 
    simplifies the sending of messages by handling the creation of the 
    messages.    
    """

    def __init__(self, output:Union[BaseLogHandler,list[BaseLogHandler]],
                 topicGenerationMethode:Optional[str]=None,
                 messageFormat:Optional[str]=None) -> None:
        """ Constructor of Logueur

        Configure the Logueur with the different output given in argument.

        Arguments:
        output : list[BaseLogHandler]
            The differents output to use for logging messages.
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

        # Initialization:
        # ---------------
        self._out = output
        self._topicGenerationMethode = topicGenerationMethode
        self._messageFormat = messageFormat

    def add_out(self, output:Union[BaseLogHandler,list[BaseLogHandler]]) -> None:
        """ Add a log output to the logueur """
        # Type Check:
        # -----------
        if not isinstance(output,(BaseLogHandler,list)):
            raise ValueError(f"The output must be BaseLogHandler or a list of BaseLogHandler (or subclass of BaseLogHandler), instead, I've received a '{type(output)}'")
        if not isinstance(output,list):
            output = [output]
        for i,out in enumerate(output,start=1):
            if not isinstance(out,BaseLogHandler):
                raise ValueError(f"Output {i} of the differents outputs must be a BaseLogHandler or a subclass of BaseLogHandler, intead I've received a '{type(out)}'")

        # Add output:
        # -----------
        self._out.append(output)

    def log(self,msg:LogMessage) -> None:
        """ Log a specific message """
        
        # Type Check:
        # -----------
        if not isinstance(msg,LogMessage):
            raise ValueError(f"The message to logged must be a LogMessage, instead I've received a '{type(msg)}'")
        
        # Logging:
        # --------
        for out in self._out:
            out.emit(msg)
    
    def debug(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ Log a message with a DEBUG level

        Construct and log a debug message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.
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
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.DEBUG,topic,fmt=format)
        self.log(msg)
    def info(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ Log a message with a INFO level

        Construct and log an info message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.
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
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.INFO,topic,fmt=format)
        self.log(msg)
    def warning(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ Log a message with a WARNING level

        Construct and log a warning message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.
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
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.WARNING,topic,fmt=format)
        self.log(msg)
    def error(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ Log a message with a ERROR level

        Construct and log an error message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.
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
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.ERROR,topic,fmt=format)
        self.log(msg)
    def fatal(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ Log a message with a FATAL level

        Construct and log a fatal message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the LogTopic class.
        If the format isn't specified, the default one will be used.
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
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.FATAL,topic,fmt=format)
        self.log(msg)


def ConsoleLogueurFactory(level:Union[str,LogLevel],filter:Union[str,LogTopicFilter]="#",
                          supportColor:bool=True, useStderr:bool=True) -> Logueur:
    """ Construct a Logueur configured with an output to the console 
    
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
    if not isinstance(level,(str,LogLevel)):
        raise ValueError(f"The level must be a str or a LogLevel, instead I've received a '{type(level)}'")
    if not isinstance(filter,(str,LogTopicFilter)):
        raise ValueError(f"The filter msut be a str or a LogLevel, instead I've received a '{type(filter)}'")
    if not isinstance(supportColor,bool):
        raise ValueError(f"The supportColor argument must be a bool, instead I've received a '{type(supportColor)}'")
    if not isinstance(useStderr,bool):
        raise ValueError(f"The supportColor argument must be a bool, instead I've received a '{type(useStderr)}'")
    
    # Type conversion:
    # ----------------
    if isinstance(level,str):
        level = LogLevel[level]
    if isinstance(filter,str):
        filter = LogTopicFilter(filter)

    # Create output:
    # --------------
    out = ConsoleLogHandler(level, filter, supportColor, useStderr)
    return Logueur([out])