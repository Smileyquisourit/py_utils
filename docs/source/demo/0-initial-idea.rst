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

- **`Database`**:  
  This class handles creating and interacting with a local SQLite database that stores all the five-letter English words used in Wordle.  
  It provides methods to create and populate the database, and to query the stored data.

- **`Search`**:  
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
