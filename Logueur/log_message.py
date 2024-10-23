# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# A log message's topic and a topic filter
# ---------------------------------------------------------
# ./Logueur/log_message.py

""" Module log_topic

Implement the LogMessage class, encapsulating all of the 
relevant informations of a log message.
"""

from typing import Optional

from .log_level import LogLevel
from .log_topic import LogTopic

class LogMessage():
    """ LogMessage

    An instance of this class represent a log message, encapsulating
    all of the relevant information about this peculiar message :
    - It's level
    - It's topic
    - The actual message to dispay
    """

    _msg_fmt = "[{level}] {topic}\n{body}\n\n"

    @property
    def msg_fmt(self) -> str:
        """ The string to use for formatting the log message.

        Should at least contains '{body}'
        """
        return self._msg_fmt
    @msg_fmt.setter
    def msg_fmt(self, msg_fmt:str) -> None:
        """ The string to use for formatting the log message.

        Should at least contains '{body}', and will be formatted
        using str.format(body=self.body,level=self.level,topic=self.topic.topic)
        """
        if not isinstance(msg_fmt,str):
            raise ValueError(f"The msg_fmt must a str, instead I've received a '{type(msg_fmt)}'")
        if not r'{body}' in msg_fmt:
            raise ValueError("The msg_fmt must at least contains {body} !")
        self._msg_fmt = msg_fmt

    def __init__(self, body:str, level:LogLevel, topic:LogTopic, fmt:Optional[str]) -> None:
        """ Constructor of LogMessage

        Construct a log message.

        Arguments:
        body : str
            The message to print in the log
        level : LogLevel
            The level of the message
        topic : LogTopic
            The topic of the message
        fmt : Optional[str]
            The format to use for formatting the message
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the log message must be a str, instead I've received '{type(body)}'")
        if not isinstance(level,LogLevel):
            raise ValueError(f"The level of the log message must be a LogLevel, instead I've received '{type(level)}'")
        if not isinstance(topic,LogTopic):
            raise ValueError(f"The topic of the log message must be a LogTopic, instead I've received '{type(topic)}'")
        if fmt and not isinstance(fmt,str):
            raise ValueError(f"The format of the log message must be a str, instead I've received '{type(fmt)}'")
        
        # Save arguments:
        # ---------------
        self.body = body
        self.level = level
        self.topic = topic
        
        if fmt:
            self.msg_fmt = fmt

    def __str__(self) -> str:
        """ Format the message with the formating string """
        return self.msg_fmt.format(body=self.body,level=self.level.name,topic=self.topic.topic)