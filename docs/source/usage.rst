Usage
=====

Installation
------------

To install `py_utils`, you need to clone the repository from GitHub and install it manually:

.. code-block:: console

   (.venv) $ git clone https://github.com/Smileyquisourit/py_utils.git
   (.venv) $ cd py_utils
   (.venv) $ pip install .

Alternatively, you can install it directly using pip with the Git URL:

.. code-block:: console

    (.venv) $ pip install git+https://github.com/Smileyquisourit/py_utils.git

Make sure you have git and pip installed on your system before running these commands.

Quick Start
-----------

Logueur
'''''''

There are different ways to log messages using a centralized structure: the `Logueur`. It offers many customization options for output (console, file, etc.), 
message formatting, and filtering by log level or topic. See :doc:`logueur` for more details.

While this flexibility allows you to tailor logging to your specific needs, here’s a quick way to get started with logging messages to the console:

.. code-block:: python

    from py_utils import Logueur
    log = Logueur.ConsoleLogueurFactory(
        "INFO",            # the level to use for filtering message
        filter="#",        # the filter to use for filtering message
        supportColor=True, # format the message using color depending on it's level
        useStderr=True     # use stderr instead of stdout for warning, error and fatal level
    )

The returned `log` object will output all messages at level `INFO` and above (excluding `DEBUG`), for all topics.  
Messages will be color-coded (green for INFO, yellow for WARNING, red for ERROR and FATAL).

To log a message, you can then use the following methods of the `log` object:

.. code-block:: python

    log.debug("A DEBUG message")     # Will not print the message, because the minimum level is INFO
    log.info("An INFO message")      # Will be printed in green on stdout
    log.warning("A WARNING message") # Will be printed in yellow on stderr
    log.error("An ERROR message")    # Will be printed in red on stderr
    log.fatal("A FATAL message")     # Will be printed in red on stderr


For more information on log levels and topics, see :doc:`logueur/log_level` and :doc:`logueur/log_topic`.

ConfigHelper
''''''''''''

The `ConfigHelper` object can read configuration data from various sources such as files, dictionaries, or strings. It 
supports JSON and a custom INI-like format. Each configuration entry can belong to a section and may optionally specify 
a type (default is `str`).

Here is an example configuration file using the custom INI format:

*app/app.conf*

.. code-block:: text

    language:str = en
    debug:bool = False

    [user]
    timeout:int = 30
    language = fr

    [admin]
    debug:bool = True
    timeout:int = 15

You can load this configuration as follows:

.. code-block:: python

    from py_utils import ConfigHelper

    conf = ConfigHelper()
    conf.read("app/app.conf")

And access the variables in the following ways:

.. code-block:: python

    # like an object:
    user_timeout = conf.user.timeout

    # like a dict:
    admin_timeout = conf["admin"][timeout]

    # Or a mix of the two:
    admin_debug = conf["admin"].timeout
    admin_debug = conf.admin["timeout"]

To define default values, simply place them before any section in the config file.  
These defaults can be accessed directly or inherited by sections that don’t override them:

.. code-block:: python

    user_debug = conf.user.debug   # = False, from the default
    admin_debug = conf.admin.debug # = True, from the 'admin' section
    default_debug = conf.debug     # = False

