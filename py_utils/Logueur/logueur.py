# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# A log message's topic and a topic filter
# ---------------------------------------------------------
# ./Logueur/logueur.py

""" 
The `Logueur` class is the main interface to log and route the messages of the application. This
class follows the `Singleton` pattern, ensuring that only one instance of `Logueur` can exist at
any given time. The method used to log a message is a class method, that receive a single 
:class:`LogMessage` instance, enabling the following logic:

    *When a message is logged, the log method first check if an instance of Logueur exist.*
    *If no instance is found, log send the message to the default handler, wich is a console*
    *handler, else it send it to the handlers registered in the Logueur instance.*

The handler is the object responsible for filtering, formatting and writting the message to the
output, and will be discussed more in detail in the Log Output section. The user can register multiple
handlers, effectively sending the message to different output, and configure each one differently. The
default handler is a console handler, that send the message to the console (via stderr). It's configured
in the following way:

- The severity level is `WARNING`,
- The topic filter is `'#'`, meaning all topics are accepted,
- The formatted messages are printed to `stderr`.

To register a different output, you can either use the :func:`ConsoleLogueurFactory` wich create
a `Logueur` instance with a user configured console handler, or create manually a handler and register it
with the :meth:`Logueur.register_output` method.

When using the :meth:`Logueur.log` method to send a message, you have to create manually a :class:`LogMessage`
instance. Altought this give you complete control as to how tme message is created, it can rapidly
became cumbersome. The :class:`Logueur` class implement 5 methods to create such :class:`LogMessage`
and calling the :meth:`Logueur.log` method, where you give the body of the message, and optionaly specify
the topic and the format:

- :meth:`Logueur.debug`
- :meth:`Logueur.info`
- :meth:`Logueur.warning`
- :meth:`Logueur.error`
- :meth:`Logueur.fatal`

When initializing the `Logueur`, you have to specify one or multiple handler, and you can also
specify a few other configuration, like the default format, or topic generation method.
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
import functools
from typing import Union, Optional

from .log_level import LogLevel
from .log_message import LogMessage
from .log_topic import LogTopic, LogTopicFilter
from .log_out import BaseLogHandler, ConsoleLogHandler, FileLogHandler

_default_level = LogLevel.factory("warning")
_default_filter = LogTopicFilter('#')

class Logueur():
    """
    Object for logging messages to various output. 

    The Logger class allows for managing different outputs for log messages, with each output configured differently. 
    This provide a structured logging for debugging and monitoring application behavior. It also simplifies the sending 
    of messages by handling the creation of the messages, although you can also define your own LogMessage and log it
    with the classmethod `log`.

    .. warning:: The Logueur class is a Singleton, but doesn't implement well this pattern, so a second
        call to the Logueur.__init__() (ie Logueur()) will errase the previous instance instead of returning it!
    """

    _default = ConsoleLogHandler(_default_level,_default_filter,supportColor=False,useStderr=True)
    _instance = None

    def __new__(cls,*args,**kwargs):

        if not cls._instance:
            cls._instance = object.__new__(cls)
            #cls._instance.__init__(*args,**kwargs)
        return cls._instance

    def __init__(self, output:Union[BaseLogHandler,list[BaseLogHandler]],
                 topicGenerationMethode:str='module',
                 messageFormat:str='[{level}] {topic}\n{body}\n\n',
                 tz:Optional[datetime.timezone]=None) -> None:
        """

        Configure the Logueur with the different output given in argument. You can also specify some
        default behavior used with the differents logging methods: the topic generation method used
        when no topic are providied, the format of the message when it isn't specified, and the timezone
        info to used when generating the message.

        This last one, the time zone info, is only configurable here, as it make more sens to have the same
        for all log messages.

        :param output: The destination of the log's messages. Shall be a 
            class herited of the BaseLogHandler or a list of object herited from BaseLogHandler in case of 
            mulitple destination.
        :type output: BaseLogHandler, list[BaseLogHandler]

        :param topicGenerationMethod: A string used to determine how to generate the topic of the 
            message. Can be 'stack' or 'module', see :mod:`~py_utils.Logueur.log_topic`. Default to `'module'`.
        :type topicGenerationMethod: str

        :param messageFormat: A string to be used to format the message before emitting it to the differents 
            output. The formatting fubnction used is `str.format` called with `level=msg_level` (the level of 
            the log entry), `body=msg_body` (the text of the entry), and `topic=msg_topic` (the topic of the 
            entry). Default to `"[{level}] {topic}\\n{body}\\n\\n"`.
            Note: the `body` must be present in the format !
        :type messageFormat: str

        :param tz: The timezone used to compute time when creating a message.
        :type tz: datetime.timezone, optional
        """

        # Type Check:
        # -----------

        # Output:
        if not isinstance(output,(BaseLogHandler,list)):
            raise TypeError(f"The output must be BaseLogHandler or a list of BaseLogHandler (or subclass of BaseLogHandler), instead, I've received a '{type(output)}'")
        if not isinstance(output,list):
            output = [output]
        for i,out in enumerate(output,start=1):
            if not isinstance(out,BaseLogHandler):
                raise TypeError(f"Output {i} of the differents outputs must be a BaseLogHandler or a subclass of BaseLogHandler, intead I've received a '{type(out)}'")
        
        # Topic generation method:
        if not isinstance(topicGenerationMethode,str):
            raise TypeError(f"The topic generation method must be a str, instead I've received a '{type(topicGenerationMethode)}'")
        if not topicGenerationMethode in LogTopic._fromMethode:
            raise ValueError(f"The topic generation method must be one of the following: {LogTopic._fromMethode}, instead I've received '{topicGenerationMethode}'")
        
        # Log message format:
        if messageFormat and not isinstance(messageFormat,str):
            raise TypeError(f"The message format must be a str, instead I've received a '{type(messageFormat)}'")
        if messageFormat and not r'{body}' in messageFormat:
            raise ValueError("The msg_fmt must at least contains {body} !")
        
        # Timezone
        if tz and not isinstance(tz,datetime.timezone):
            raise TypeError(f"The timezone info (tz) must be a datetime.timezone or None, instead I've received a '{type(tz)}'")

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
        Manually add one ore multiple log output (handlers) to the logueur.
        
        :param output: The destination of the log's messages. Shall be a class herited
            of the BaseLogHandler or a list of object herited from BaseLogHandler in
            case of mulitple destination.
        :type output: BaseLogHandler, list[BaseLogHandler]
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
        Log a specific message. If a instance of Logueur is defined, use its outputs, else
        use the default one.
        
        :param msg: The message to log.
        :type msg: LogMessage
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
        Log a message with a DEBUG level

        Construct and log a debug message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the :class:`~py_utils.Logueur.log_topic.LogTopic` class.
        If the format isn't specified, the default one will be used.

        :param body: The text of the message.
        :type body: str

        :param topic: The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :type topic: optional, str
        
        :param format: The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`~py_utils.Logueur.log_message.LogMessage`
        :type format: optional, str
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        elif topic:
            topic = LogTopic(topic)
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        elif not format:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.DEBUG,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def info(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        Log a message with a INFO level

        Construct and log an info message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the :class:`~py_utils.Logueur.log_topic.LogTopic` class.
        If the format isn't specified, the default one will be used.

        :param body: The text of the message.
        :type body: str

        :param topic: The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :type topic: optional, str

        :param format: The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`~py_utils.Logueur.log_message.LogMessage`.
        :type format: optional, str
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        elif topic:
            topic = LogTopic(topic)
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        elif not format:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.INFO,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def warning(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        Log a message with a WARNING level

        Construct and log a warning message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the :class:`~py_utils.Logueur.log_topic.LogTopic` class.
        If the format isn't specified, the default one will be used.

        :param body: The text of the message.
        :type body: str

        :param topic: The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :type topic: optional, str

        :param format: The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`~py_utils.Logueur.log_message.LogMessage`.
        :type format: optional, str
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        elif topic:
            topic = LogTopic(topic)
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        elif not format:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.WARNING,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def error(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        Log a message with a ERROR level

        Construct and log an error message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the :class:`~py_utils.Logueur.log_topic.LogTopic` class.
        If the format isn't specified, the default one will be used.

        :param body: The text of the message.
        :type body: str

        :param topic: The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :type topic: optional, str

        :param format: The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`~py_utils.Logueur.log_message.LogMessage`.
        :type format: optional, str
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        elif topic:
            topic = LogTopic(topic)
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        elif not format:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.ERROR,topic,fmt=format,tz=self._timezone)
        self.log(msg)
    def fatal(self, body:str, topic:Optional[str]=None, format:Optional[str]=None) -> None:
        """ 
        Log a message with a FATAL level

        Construct and log a fatal message. If the topic isn't specified, one is
        constructed with the topicFactory class method of the :class:`~py_utils.Logueur.log_topic.LogTopic` class.
        If the format isn't specified, the default one will be used.

        :param body: The text of the message.
        :type body: str

        :param topic: The topic of the message. If no topic are specified, use the topic
            factory function of the specified `topicGenerationMethod`. Default
            is `module`.
        :type topic: optional, str

        :param format: The format to be used when generating the message. If not specified,
            use the format specified in the constructor (`messageFormat`). See
            :class:`~py_utils.Logueur.log_message.LogMessage`.
        :type format: optional, str
        """

        # Type Check:
        # -----------
        if not isinstance(body,str):
            raise ValueError(f"The body of the message must be a str, instead I've received a '{type(body)}'")
        if topic and not isinstance(topic,str):
            raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
        elif topic:
            topic = LogTopic(topic)
        else:
            topic = LogTopic.topicFactory(self._topicGenerationMethode, 3)
        if format and not isinstance(format,str):
            raise ValueError(f"The format of the message must be a str, instead I've received a '{type(format)}'")
        elif not format:
            format = self._messageFormat
        
        # Create and log message:
        # -----------------------
        msg = LogMessage(body,LogLevel.FATAL,topic,fmt=format,tz=self._timezone)
        self.log(msg)

    @classmethod
    def get_loggingFunc(cls,topicGenMethode:str='module',
                        fmt:str='[{level}] {topic} :: {body}\n',
                        tz:Optional[datetime.timezone]=None) -> callable:
        """
        Return a function to log message without having to initialise a handler before.

        This returned function mimic the behavior of the :meth:`~Logueur.debug`, :meth:`~Logueur.info`, 
        :meth:`~Logueur.warning`, :meth:`~Logueur.error` and :meth:`~Logueur.fatal` methods of the 
        `Logueur` class, but take the level as an additional argument.

        The topic generation methode ('topicGenMethode') argument enable the optionality of the topic
        argument of the returned function. If the topic provided to the returned function is `None`, 
        it will be generated by the methode specified by 'topicGenMethode'.

        :param topicGenMethode: The methode to generate the default topic of the logged messages.
            Default to 'module'.
        :type topicGenMethode: str

        :param fmt: The format to use when writting the message. It must contain at least `{body}`.
            See :class:`~py_utils.Logueur.log_message.LogMessage`. Default to '[{level}] {topic} :: {body}\\n'
        :type fmt: str

        :param tz: The timezone information to use when computing the datetime of the creation
            of the message.
        :type tz: datetime.timezone, optionnal

        :return: A function to log messages.
        :rtype: callable
        """

        # Type/Value check:
        # -----------------
        if not isinstance(topicGenMethode,str):
            raise TypeError(f"The topic generation methode (topicGenMethode) must be a str, instead I've received {type(topicGenMethode)}")
        if not topicGenMethode in LogTopic._fromMethode:
            raise ValueError(f"The topic generation method (topicGenMethode) must be one of the following: {LogTopic._fromMethode}, instead I've received '{topicGenMethode}'")
        if not isinstance(fmt,str):
            raise TypeError(f"The message format must be a str, instead I've received a '{type(messageFormat)}'")
        if not r'{body}' in fmt:
            raise ValueError("The msg_fmt must at least contains {body} !")
        if tz and not isinstance(tz,datetime.timezone):
            raise TypeError(f"The timezone info (tz) must be a datetime.timezone or None, instead I've received a '{type(tz)}'")

        # Logging function:
        # -----------------
        def log(level:Union[str,int,LogLevel],body:str, 
                topic:Optional[Union[str,LogTopic]]=None):
            """
            Log a message to the logs, either the default one or the one configured by the user.

            Parameters
            ----------
            :param level: The level of the message.
            :type level: LogLevel, str, int

            :param body: The body of the message.
            :type body: str

            :param topic: The topic of the message, if `None`, the topic generation method specified
                in the `get_loggingFunction` will be used to generate it.
            """

            # Type check
            if not isinstance(level,(str,int,LogLevel)):
                raise TypeError(f"The 'level' should be a 'str', 'int', or 'LogLevel', instead I've received a {type(level)}")
            if topic and not isinstance(topic,str):
                raise ValueError(f"The topic of the message must be a str, instead I've received a '{type(topic)}'")
            elif topic and isinstance(topic,str):
                topic = LogTopic(topic)
            else:
                topic = LogTopic.topicFactory(topicGenMethode, 3)

            msg = LogMessage(
                body=body,
                level=LogLevel.factory(level),
                topic=topic,
                fmt=fmt,
                tz=tz
            )

            cls.log(msg)

        #functools.update_wrapper(Logueur.get_loggingFunc, log)
        return log


def ConsoleLogueurFactory(level:Union[str,LogLevel],filter:Union[str,LogTopicFilter]="#",
                          supportColor:bool=True, useStderr:bool=True) -> Logueur:
    """    
    Construct a Logueur configured with an output to the console.
    
    :param level: The level used for filtrate log messages.
    :type level: LogLevel, str

    :param filter:
        The topic filtrer used for filtrate log messages. Default to `'#'` (all topics).
    :type filter: LogTopicFilter, str
    :param supportColor: If the console support color, and if colors should be used.
        Default to `True`.
    :type supportColor: bool
    :param useStderr: `True` to use stderr for warning, error and fatal message.
        Default to `True`.
    :type useStderr: bool


    :return: The constructed Logueur instance.
    :rtype: Logueur
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