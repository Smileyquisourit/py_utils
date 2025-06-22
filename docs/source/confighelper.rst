Configuration Framework
=======================

.. automodule:: py_utils.ConfigHelper
   :no-members:
   :noindex:

Format of configuration
-----------------------

The :class:`~py_utils.ConfigHelper.confighelper.ConfigHelper` can read 2 format of configuration.
The first one is a *modified INI format*, of wich the following exemple is given:

.. code-block:: ini

   langage:str = en
   debug:bool = False

   [user]
   timeout:int = 30
   langage = fr

   [admin]
   debug:bool = True
   timeout:int = 15

Contents
--------

To learn more about the 3 main part of a configuration, see the detailed documentation below.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   confighelper/confighelper
   confighelper/config_section
   confighelper/config_variable