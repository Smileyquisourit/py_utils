# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Initialisation of Logueur
# ---------------------------------------------------------
# py_utils/Logueur/__init__.py

"""
The `Logueur` module implements a logging framework intended to be flexible enough to support projects 
of all sizes — from small prototypes to large-scale applications — throughout their entire lifecycle. 
The primary interface for logging messages is the :class:`~py_utils.Logueur` class.

This framework provides two main filtering mechanisms for log messages:

1. **Log level**: Each message has a severity level, which determines whether it should be processed.
   The available levels are:

   - DEBUG (0): Detailed diagnostic information.
   - INFO (1): General information about normal operations.
   - WARNING (2): A sign that something unexpected occurred, but the application can continue.
   - ERROR (3): A serious issue that affects part of the application.
   - FATAL (4): A critical error that leads to application termination.

   When a minimum log level is specified, messages below that level are ignored.

2. **Topic-based filtering**: Each log message can be assigned a topic, which can either be explicitly set
   by the developer or automatically inferred from the module or the execution stack. Topics provide a powerful 
   way to categorize and filter logs. See :doc:`logueur/log_topic` for more details.

Log messages can be directed to different output targets. The system provides three built-in log outputs:

- **Console output** (standard output or error stream),
- **Plain file output** (logs are written to a regular file in a text format),
- **Rotating file output** (logs are written to a file with automatic rotation based on size or time).

Each of these output types is implemented as a separate class, all inheriting from a common abstract base class. 
This makes it easy to create custom outputs by subclassing and implementing your own logic. See 
:doc:`logueur/log_out` for more details on available outputs and customization.

The :class:`Logueur` class follows the Singleton pattern and provides a centralized logging interface. 
It manages a set of log outputs (handlers), which determine where log messages are written. By default, 
if no outputs are explicitly configured by the user, log messages are printed to the console. However, 
if one or more outputs are set manually, those will override the default behavior.

Additionally, the class exposes a method that returns a pre-configured logging function. This function 
can be used to log messages in a simplified way, without directly interacting with the `Logueur` instance. 
It is especially useful in modules or external packages, where developers want to emit logs that are 
properly routed through the central logging configuration. This design ensures consistency and allows 
modular components to log messages without needing to know how the logging system is set up.

"""

__all__ = [
    "Logueur", "ConsoleLogueurFactory", "LogLevel", "ConsoleLogHandler", "FileLogHandler", 
    "RotaryFileLogHandler", "LogTopicFilter"
]

# Expose main interfaces:
# -----------------------

from .logueur import Logueur, ConsoleLogueurFactory
from .log_level import LogLevel
from .log_out import ConsoleLogHandler, FileLogHandler, RotaryFileLogHandler
from .log_topic import LogTopicFilter


# TODO: See the doc and the logics of Logueur.getLogFunc, it seem to be something wrong
# with the topic and topic generation method.