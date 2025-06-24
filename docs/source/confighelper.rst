Configuration Framework
=======================

.. automodule:: py_utils.ConfigHelper
   :no-members:
   :noindex:

Format of Configuration
-----------------------

The :class:`~py_utils.ConfigHelper.confighelper.ConfigHelper` class supports two formats for reading 
configuration data.

**1. Modified INI Format**

The first format is a custom variation of the traditional INI format. Here is an example:

.. code-block:: ini

   langage:str = en
   debug:bool = False

   [user]
   timeout:int = 30
   langage = fr

   [admin]
   debug:bool = True
   timeout:int = 15

The first two variables (`langage` and `debug`) are defined as default variables, meaning they will 
be available in every section unless explicitly overridden.

For instance:

- In the `user` section, the `langage` variable is overridden and set to `'fr'`.
- In the `admin` section, since no override is provided for `langage`, it retains its default value `'en'`.

The type of each variable can be specified using a colon (`:`), such as `timeout:int = 30`. If no 
type is provided, it defaults to `str`.

Comments are supported, but only for an entire line. The comments indicators are `#` and `;`, but can be change
before reading a configuration file.

.. note:: The :class:`~py_utils.ConfigHelper.ConfigHelper` can also read :class:`str` and expect the same format.

**2. JSON Format**

The second supported format is a structured JSON representation. The previous configuration example 
would be written as follows:

.. code-block:: json

   {
      "DEFAULTS": [
         {"name": "langage", "type": "str", "value": "en"},
         {"name": "debug", "type": "bool", "value": "False"}
      ],
      "SECTIONS": [
         {
            "user": [
               {"name": "timeout", "type": "int", "value": 30},
               {"name": "langage", "value": "fr"}
            ]
         },
         {
            "admin": [
               {"name": "debug", "type": "bool", "value": "True"},
               {"name": "timeout", "type": "int", "value": 15}
            ]
         }
      ]
   }

In this format:

- Default variables are listed under the `"DEFAULTS"` key.
- Configuration sections are listed under the `"SECTIONS"` key, each represented as a dictionary with the section name as key and a list of variables as value.
- All variables of one section are regrouped in a list, and each variable is represented by a dictionary contening a `name` and `value` keys, and optionnaly a `type` key.
- The `type` field is optional and defaults to `"str"` if omitted.

Both formats are interchangeable and serve the same purpose: organizing structured, typed configuration 
data across reusable sections with sensible defaults. This enable you to define a JSON document with a
default configuration, and then override it with a user defined configuration, in either format.

.. note:: The :class:`~py_utils.ConfigHelper.ConfigHelper` can also read :class:`dict` and expect the same structure.

Contents
--------

To learn more about the 3 main part of a configuration, see the detailed documentation below.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   confighelper/confighelper
   confighelper/config_section
   confighelper/config_variable