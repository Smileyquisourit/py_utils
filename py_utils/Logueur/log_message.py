# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# A log message's topic and a topic filter
# ---------------------------------------------------------
# ./py_utils/Logueur/log_message.py

""" 
================
Module log_topic
================

Implement the LogMessage class, encapsulating all of the relevant informations of a log message.
"""

import datetime
from typing import Optional

from .log_level import LogLevel
from .log_topic import LogTopic

class LogMessage():
    """ 
    ==========
    LogMessage
    ==========

    An instance of this class represent a log message, encapsulating
    all of the relevant information about this peculiar message

    - It's level
    - It's topic
    - The actual message to dispay
    - The datetime of it's creation

    An instance of this class also contains the format of the message to
    be used, the default is
        `[{level}] {topic}\\n{body}\\n\\n`
    """

    _msg_fmt = "[{level}] {topic}\n{body}\n\n"

    @property
    def msg_fmt(self) -> str:
        """ The string to use for formatting the log message.

        Should at least contains '{body}', and will be formatted
        using 
            `str.format()`
        called with 'body', 'level', 'topic', 'date', and 'time'
        """
        return self._msg_fmt
    @msg_fmt.setter
    def msg_fmt(self, msg_fmt:str) -> None:
        if not isinstance(msg_fmt,str):
            raise TypeError(f"The msg_fmt must a str, instead I've received a '{type(msg_fmt)}'")
        if not r'{body}' in msg_fmt:
            raise ValueError("The msg_fmt must at least contains {body} !")
        self._msg_fmt = msg_fmt

    def __init__(self, body:str, level:LogLevel, topic:LogTopic, fmt:Optional[str]=None, 
                 tz:Optional[datetime.timezone]=None) -> None:
        """ Constructor of LogMessage

        Construct a log message. If no format (`fmt`) is specified, the default one is used:
        
        `[{level}] {topic}\\n{body}\\n\\n`

        When creating a log message, the time is computed (using datetime.datetime.now()) and is passed when
        formating the message. 2 options are passed along with the ones of the default format:
        - 'date' = datetime.datetime.now().date().isoformat()
        - 'time' = datetime.datetime.now().timetz().isoformat()

        parameters
        ----------
        :param body: The message to print in the log
        :type body: str

        :param level: The level of the message
        :type level: LogLevel

        :param topic: The topic of the message
        :type topic: LogTopic

        :param fmt: The format to use for formatting the message
        :type fmt: str, optional

        :param tz: The timezone to use when generating the datetime object.
        :type tz: datetime.timezone, optional
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise TypeError(f"The body of the log message must be a str, instead I've received '{type(body)}'")
        if not isinstance(level,LogLevel):
            raise TypeError(f"The level of the log message must be a LogLevel, instead I've received '{type(level)}'")
        if not isinstance(topic,LogTopic):
            raise TypeError(f"The topic of the log message must be a LogTopic, instead I've received '{type(topic)}'")
        if fmt and not isinstance(fmt,str):
            raise TypeError(f"The format of the log message must be a str, instead I've received '{type(fmt)}'")
        if tz and not isinstance(tz,datetime.timezone):
            raise TypeError(f"The timezone used in the log message must be a datetime.timezone, instead I've received '{type(tz)}'")
        
        # Save arguments:
        # ---------------
        self.body = body
        self.level = level
        self.topic = topic
        
        if fmt:
            self.msg_fmt = fmt

        # Compute other arguments:
        # ------------------------
        self.datetime = datetime.datetime.now(tz)

    def __str__(self) -> str:
        """ Format the message with the formating string """
        args = {
            'body' : self.body,
            'level': self.level.name,
            'topic': self.topic.topic,
            'date' : self.datetime.date(),
            'time' : self.datetime.timetz()
        }
        return self.msg_fmt.format(**args)