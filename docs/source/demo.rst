=======================
Getting Started Example
=======================

This example showcases how to use the :mod:`py_utils` package in a real-world scenario by developing a simple application
that solves the New York Times Wordle game.

To better illustrate the use cases of the :doc:`logueur` and the :doc:`confighelper`, this example is organized into:
a *core* submodule, which contains the main business logic, and two application layers — *cli* and *gui* —
which build on top of this core logic. This way:


- The *core* submodule demonstrates how to integrate :mod:`py_utils` into a reusable library or business logic layer.
  In particular, it shows how to configure and retrieve a default logger that seamlessly uses the user’s own logging setup,
  or falls back to console output when needed.

- The *cli* submodule is a simple command-line application built on top of *core*. It shows a basic use case
  of the logging utility provided by :mod:`py_utils` to build a small but complete Python application with console logging.

- The *gui* submodule is a simple graphical interface built on top of *core*. It illustrates how to use the configuration
  utility provided by :mod:`py_utils` along with additional features of the logging framework.

Together, these examples show how you can use :mod:`py_utils` to structure your own Python projects with clear, reusable modules
and robust logging and configuration handling. Together, these examples show how you can use :mod:`py_utils` to structure your own 
Python projects with clear, reusable modules and robust logging and configuration handling.

Feel free to explore, adapt, and run the demo to see how everything fits together in practice.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   demo/0-initial-idea
   demo/1-database
   demo/2-search
   demo/3-cli

