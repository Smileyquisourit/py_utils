# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Initialisation of Logueur
# ---------------------------------------------------------
# ./Logueur/__init__.py

"""
    =======
    Logueur
    =======

    This module provides a logging framework. The log can have multiple destination,
    like a the console or a file.

    Objects
    -------

    Logueur:
        The main object of the module. Used for logging messages to various output.
        It's also responsible of creating the log's messages.
    LogLevel:
        A Enum class representing all the supported log's messages level.
    LogMessage:
        Encapsulate all of the relevant informations of a log message.
    LogTopic:
        Contains the topic of a log message. This class also implement a static method 
        for generating a log topic from the execution stack.
    LogTopicFilter:
        Filter for log message's topic.

    Their is multiple log's destination (the console, a file, ...). See :mod:`Logueur.log_out`
    for more information.

    Functions
    ---------
    ConsoleLogueurFactory:
        Construct a Logueur configured with an output to the console.
"""

# Expose main interfaces:
# -----------------------

from .logueur import Logueur, ConsoleLogueurFactory
from .log_level import LogLevel
from .log_out import ConsoleLogHandler, FileLogHandler
from .log_topic import LogTopicFilter