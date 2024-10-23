# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Initialisation of Logueur
# ---------------------------------------------------------
# ./Logueur/log_level.py

""" Module log_topic

Implement the LogTopic class, a class representing the topic
of a log message, and the LogTopicFilter class, a class representing
a filter for log message's topic.
"""

import re
import inspect
from typing import Optional

def _generateFromStack(n_frame:int) -> str:
    """
    Generate the topic by concatening the 'function'
    property of each FrameInfo of the execution stack returned by
    the function inspect.stack(). The topic start with the outermost
    frame's function, and each function name are separated by a dot.
    
    Ignore the first 'n_frame'. 
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
    generate the topic in the following form:
        'module_name.class_name.methode_name' or
        'module_name.function_name'

    The frame used to get the module, class, methode
    or function name is specified by using n_frame
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



class LogTopic():
    """ LogTopic

    The topic of a log message. An instance of this class contains
    the topic of a log message. This class also implement a static
    method for generating a log topic from the execution stack.

    A topic is a string constitued of different keys, separated with
    a dot: 'key1.key2. ... .keyN'

    A log message topic is like a tag, that can be used to filtrate
    the different messages.
    """

    _fromMethode = ["stack","module"]

    def __init__(self, topic:str) -> None:
        """ Constructor of LogTopic.

        A log message topic is like a tag, that can be used to
        filtrate the different messages.

        Arguments:
        topic : str
            The topic of the log message
        """

        # Type Check:
        # -----------
        if not isinstance(topic, str):
            raise ValueError(f"The topic must be a str, instead I've received a '{type(topic)}'")
        
        # Save topic:
        # -----------
        self.topic = topic

    @classmethod
    def topicFactory(cls, method:Optional[str], n_frame:int=1) -> 'LogTopic':
        """ Generate a log topic from the execution stack.

        This static method use the inspect module to inspect
        the execution stack. It ignore the first n_frame given
        in argument.

        This function generate the topic by using 2 methods, that
        the user can choose:
        
        - by 'stack': generate the topic by concatening the 'function'
        property of each FrameInfo of the execution stack returned by
        the function inspect.stack(). The topic start with the outermost
        frame's function, and each function name are separated by a dot.

        - by 'module': generate the topic in the following form:
        'module_name.class_name.methode_name' or
        'module_name.function_name'

        Arguments:
        n_frame : int
            Dependending of the methode used, represent the number of
        frame to ignore ('stack' method) or the frame to use ('module'
        method)
        method : Optional[str]
            The method to use for generating the topic. Must be member of
        ["stack","module"]. Default is "module"

        Return:
        topic : LogTopic
            The topic generated.
        """

        # Type Check:
        # -----------
        if not isinstance(n_frame,int):
            raise ValueError(f"The agument n_frame must be a int, instead I've received a '{type(n_frame)}'")
        if method and not isinstance(method,str):
            raise ValueError(f"The agument method must be a str, instead I've received a '{type(method)}'")
        else:
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
    """ LogTopicFilter

    Filter for log message's topic. An instance of this class enable 
    the user to exclude log message using a form of regexp.

    The following wildcard are supported:
    - '*' replace 1 key
    - '#' replace 0 to N words
    """

    def __init__(self, filter:str) -> None:
        """ Constructor of LogTopicFilter

        Construct an instance of LogTopicFilter with the input string
        'filter'. The pattern used to filtrate the different log messages's
        topic is then computed by replacing the wildcards by their corresponding
        expression.

        Arguments:
        filter : str
            The string used for constructing the filter.
        """

        # Type Check:
        # -----------
        if not isinstance(filter,str):
            raise ValueError(f"The filter must be a str, instead I've received a '{type(filter)}'")
        
        # Construct Pattern:
        # ------------------
        self._orig_filter = filter
        pattern = filter.replace('.',r'\.')
        pattern = pattern.replace('*',r'[^\.]+')
        pattern = pattern.replace('#',r'.*')
        self.pattern = re.compile(pattern)

    def match(self,topic:LogTopic) -> bool:
        """ Check if the given topic match the filter.

        Argument:
        topic : LogTopic
            The topic to check

        Return:
        match : bool
            True if the topic match, False otherwise
        """

        # Type Check:
        # -----------
        if not isinstance(topic,LogTopic):
            raise ValueError(f"The topic must be a LogTopic, instead I've received a '{type(topic)}'")

        # Match Check:
        # ------------
        if self.pattern.match(topic.topic):
            return True
        else:
            return False
