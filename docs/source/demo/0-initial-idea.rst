================
0 - Initial Idea
================

About Wordle
------------

Wordle is a popular word puzzle game published daily by the New York Times.  
The goal is to guess a hidden five-letter English word within six attempts.  
After each guess, the game provides feedback for each letter:

- 🟩 A green tile means the letter is in the correct position.
- 🟨 A yellow tile means the letter is in the word but in a different position.
- ⬜ A grey tile means the letter is not in the word at all.

Players use these clues to narrow down possible words and find the correct answer.  
The logic behind this process — filtering words based on known and excluded letters — is exactly what this demo application replicates programmatically.

The idea
--------

To solve the Wordle game, we will use Python’s standard :mod:`sqlite3` module to create a database
containing all the five-letter words used by Wordle. We will develop a simple class to create and interact
with this database, and a second class to perform searches on it.  
Then, we will build a *Command Line Interface* (CLI) and a *Graphical User Interface* (GUI)
that use this core logic to help find the correct word.

This application is organized into three main parts: the **core module**, the **CLI module**, and the **GUI module**.

Core module
~~~~~~~~~~~

The *core* submodule contains the main business logic of the application.  
It is designed to mimic a real-world reusable module: it uses only the default logging functionality,
without defining its own :class:`~py_utils.logueur.Logueur`.

It includes two main classes:

- **`WordleDatabase`**:  
  This class handles creating and interacting with a local SQLite database that stores all the five-letter English words used in Wordle.  
  It provides methods to create and populate the database, and to query the stored data.

- **`WordleSearch`**:  
  This class performs searches for possible Wordle words based on user-provided hints (e.g. known letters, excluded letters, or letter positions).

CLI module
~~~~~~~~~~

The *cli* submodule provides a simple command-line interface to interact with the core logic.  
As an application layer, it defines its own :class:`~py_utils.logueur.Logueur` instance.  
It exposes functions to:

- **Create and build the database**:  
  Download a word list (for example, a `.txt` file from GitHub) and populate the local SQLite database.

- **Search for words**:  
  Run queries against the database using search criteria (e.g. known letters, positions, exclusions).

GUI module
~~~~~~~~~~

TODO


Files organisation and preparations
-----------------------------------

This is the architecture of the example ::

    ├── demo/
    │   ├── pyproject.toml
    │   ├── WordleSolver/
    │   │   ├── cli/
    │   │   ├── core/
    │   │   │   ├── database.py
    │   │   │   ├── search.py
    │   │   │   └── __init__.py
    │   │   ├── gui/
    │   │   ├── __init__.py
    │   │   ├── __main__.py

To test the application while we're developing it, we will use a *CLI* approch, that we will later transform
to make our *CLI* application. To do so, we need the *pyproject.toml* file so that *pip* can recongnize it
as a package. The *WordleSolver/__main__.py* will be our entry point, so you will need to create at least 
the following files to work the demo ::

    ├── demo/
    │   ├── pyproject.toml
    │   ├── WordleSolver/
    │   │   ├── __init__.py
    │   │   ├── __main__.py

The *pyproject.toml* file is a modern configuration file used to define build system requirements and project 
metadata for Python projects. It was introduced by PEP 518 and extended by other PEPs (like PEP 621 for 
standardized metadata) to unify Python packaging and make it easier to build, distribute, and install Python 
packages. It has many section to describe the project, but we will only be intersted is two of them for this 
project: 

- **project** section, that describes the project’s metadata
- **project.scripts** section, that declares command-line scripts that will be installed when your package is installed.

In our case, the *pyproject.toml* should at least contain the following informations:

.. code-block:: toml

 	[project]
  	name = "WordleSolver"
  	version = "0.1.0"
  	dependencies = [
		"py_utils @ git+https://github.com/Smileyquisourit/py_utils.git@dev"
  	]

  	[project.scripts]
  	WordleSolver = "WordleSolver.__main__:main"

As for the *WordleSolver/__main__.py* file, it will for now only contain a simple main function:

.. code-block:: python

  	def main():
    	print("Hello Wordle !")

  	if __name__ == "__main__":
    	main()

With this structure, we will be able to execute the :func:`main()` directly in the terminal by 
typing *WordleSolver* (from the *pyproject.toml* script definition) or like a python module,
ie by typing :

.. code-block:: bash

  	python3 -m WordleSolver

The *WordleSolver/__init__.py* file can be empty for now, it only serve to enable pip and python to 
recognize the directory as a package. To test the installation, you try to launch the :func:`main` 
function with python (like a module), or you can try to install it in editable mode.

To install it in editable mode, you can first create a virtual environment, and then install it with
*pip* and the *-e* flag :

For linux :

.. code-block:: bash

	python3 -m venv .venv
	source .venv/bin/activate

	pip install -e .

For windows:

.. code-block:: bash

	python3 -m venv .venv
	.venv\Scripts\activate.bat

	pip install -e .

In both case, you should see a *Hello Wordle !* printed on your terminal ! We can now start to code our application,
by starting with the database.