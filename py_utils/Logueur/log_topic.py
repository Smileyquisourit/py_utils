# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Log messages' topic and topic filter
# ---------------------------------------------------------
# ./py_utils/Logueur/log_level.py

""" 
================
Module log_topic
================

This module implement differents class and functions to generate, represent and filtrate log messages'
topics. These topics are constitued of different keys separate with a dot and supports a form of regex
to filtrate them.

Classes
-------
LogTopic():
    A class representing the topic of a log message, with support for equality test. This class also \
    implement a class method for generating such a topic from the stack or the module. See
        - :func:`_generateFromStack`
        - :func:`_generateFromModule`

LogTopicFilter():
    A class representing a filter for log message's topic. It implement a `match` methode using the \
    following wildcard for matching multiple keys: `'*'` and `'#'`

Function
--------
_generateFromStack:
    A function generating a str constitued of the `function` property of each `FrameInfo` of the \
    execution stack, separated by a dot.
_generateFromModule:
    A function generating a str constitued of the module name, classe name and methode name (or just \
    the function name if it's not a class method), separated by a dot.
"""

import re
import inspect
from typing import Optional, Union


# Private Functions:
# ------------------

def _generateFromStack(n_frame:int) -> str:
    """
    ===================
    Generate From Stack
    ===================

    Generate the topic by concatening the `function` property of each `FrameInfo` of the execution stack returned by
    the function `inspect.stack()`. The topic start with the outermost frame's function, and each function name are 
    separated by a dot.
    
    Ignore the first `n_frame`.

    Parameters
    ----------
    :param n_frame: The number of frame to ignore.
    :type n_frame: int

    Return
    ------
    :return: The computed topic.
    :rtype: str
    """

    # Get the stack:
    # --------------
    stack = inspect.stack()
    stack = stack[n_frame:]

    # Parse the stack:
    # ----------------
    topics = list()
    for frame_info in reversed(stack):
        if frame_info.function == "<module>":
            continue
        topics.append(frame_info.function)

    # Concatenate the topic string:
    return ".".join(topics)

def _generateFromModule(n_frame:int) -> str:
    """
    ====================
    Generate From Module
    ====================

    generate the topic in the following form

    - `module_name.class_name.methode_name`
    - `module_name.function_name`

    The frame used to get the module, class, method or function name is 
    specified by using n_frame.

    Parameters
    ----------
    :param n_frame: The frame number from wich to get the module, class, method or function name.
    :type n_frame: int

    Return
    ------
    :return str:
        The computed topic.
    """

    # Get the frame:
    # --------------
    stack = inspect.stack()
    frame_info = stack[n_frame]

    # Get the topic:
    # --------------
    topics = list()

    # Module:
    if module := inspect.getmodule(frame_info.frame):
        if '.' in module.__name__:
            topics.append(module.__name__.rsplit(".",1)[-1])
        else:
            topics.append(module.__name__)
    # Class and method:
    qualName = frame_info.frame.f_code.co_qualname
    if '.' in qualName:
        topics.append(qualName.rsplit(".",1)[0]) # class
        topics.append(qualName.rsplit(".",1)[1]) # method
    else:
        topics.append(qualName)
    
    return ".".join(topics)


# Class definitions:
# ------------------

class LogTopic():
    """ 
    ========
    LogTopic
    ========

    The topic of a log message. An instance of this class contains the topic of a log 
    message. This class also implement a static method for generating a log topic from 
    the execution stack.

    A topic is a string constitued of different keys, separated with a dot\n 
    `key1.key2. ... .keyN`

    A log message topic is like a tag, that can be used to filtrate the different messages.
    """

    _fromMethode = ["stack","module"]

    def __init__(self, topic:str) -> None:
        """ Constructor of LogTopic.

        A log message topic is like a tag, that can be used to
        filtrate the different messages.

        Parameters
        ----------
        :param topic: The topic of the log message.
        :type topic: str
        """

        # Type Check:
        # -----------
        if not isinstance(topic, str):
            raise TypeError(f"The topic must be a str, instead I've received a '{type(topic)}'")
        
        # Save topic:
        # -----------
        self.topic = topic
    def __repr__(self) -> str:
        return self.topic
    def __eq__(self,other:Union['LogTopic',str]) -> bool:
        """ Equality between 2 LogTopic """
        if not isinstance(other,(LogTopic,str)):
            return False
        
        if isinstance(other,LogTopic):
            return self.topic == other.topic
        else:
            return self.topic == other

    @classmethod
    def topicFactory(cls, method:Optional[str], n_frame:int=2) -> 'LogTopic':
        """ 
        =============
        Topic Factory
        =============
        
        Generate a log topic from the execution stack.

        This static method use the inspect module to inspect the execution stack. It ignore the 
        first n_frame given in argument. This function generate the topic by using 2 methods, that 
        the user can choose
        
        - by `stack`: generate the topic by concatening the `function` property of each `FrameInfo` 
        of the execution stack returned by the function `inspect.stack()`. The topic start with the 
        outermost frame's function, and each function name are separated by a dot.

        - by `module`: generate the topic in the following form 
            - `module_name.class_name.methode_name` or
            - `module_name.function_name`

        Parameters
        ----------

        :param method: 
            The method to use for generating the topic. Must be member of `["stack","module"]`. Default 
            is `module`.
        :type method: str or None

        :param n_frame: Dependending of the methode used, represent the number of frame to ignore
            (`stack` method) or the frame to use (`module` method). Default to `n_frame=2`.
        :type n_frame: int

        Returns
        -------
        :return: The topic generated.
        :rtype: LogTopic
        """

        # Type Check:
        # -----------
        if not isinstance(n_frame,int):
            raise TypeError(f"The agument n_frame must be a int, instead I've received a '{type(n_frame)}'")
        if method and not isinstance(method,str):
            raise TypeError(f"The agument method must be a str, instead I've received a '{type(method)}'")
        if not method:
            method = "module"
        
        # Value Check:
        # ------------
        if not method in cls._fromMethode:
            raise ValueError(f"The agument method must be in {cls._fromMethode}, instead I've received '{method}'")
        
        # Topic generation:
        # -----------------
        if method == "stack":
            topic = _generateFromStack(n_frame)
        else:
            topic = _generateFromModule(n_frame)
        
        return cls(topic)

class LogTopicFilter():
    """ 
    ==============
    LogTopicFilter
    ==============

    Filter for log message's topic. An instance of this class enable 
    the user to exclude log message using a form of regexp.

    The following wildcard are supported

    - `*` replace 1 key or part of a key
    - `#` replace 0 to N key

    """

    def __init__(self, filter:str) -> None:
        """ Constructor of LogTopicFilter

        Construct an instance of LogTopicFilter with the input string `filter`. The pattern used 
        to filtrate the different log messages's topic is then computed by replacing the wildcards 
        by their corresponding expression.
        
        The wildcard supported are:
        - `*` replace one key or part of a key
        - `#` replace any number of key, including none.

        Parameters
        ----------
        :param filter: The string used for constructing the filter.
        :type filter: str
        """

        # Type Check:
        # -----------
        if not isinstance(filter,str):
            raise TypeError(f"The filter must be a str, instead I've received a '{type(filter)}'")
        
        # Construct Pattern:
        # ------------------
        self._orig_filter = filter
        pattern = filter.replace('.',r'\.')
        pattern = pattern.replace('*',r'[^\.]+')
        pattern = pattern.replace('#',r'.*')
        self.pattern = re.compile(pattern)
    def __eq__(self,other:Union['LogTopicFilter',re.Pattern]) -> bool:
        """ Equality between 2 LogTopic """
        if not isinstance(other, (LogTopicFilter,re.Pattern)):
            return False
        
        if isinstance(other,LogTopicFilter):
            return self.pattern == other.pattern
        
        else:
            return self.pattern == other

    def match(self,topic:LogTopic) -> bool:
        """ 
        =====
        match
        =====

        Check if the given topic match the filter.

        Parameters
        ----------
        :param topic: The topic to check.
        :type topic: LogTopic

        Return
        ------
        :return: `True` if the topic match, `False` otherwise.
        :rtype: bool
        """

        # Type Check:
        # -----------
        if not isinstance(topic,LogTopic):
            raise TypeError(f"The topic must be a LogTopic, instead I've received a '{type(topic)}'")

        # Match Check:
        # ------------
        if self.pattern.fullmatch(topic.topic):
            return True
        else:
            return False
