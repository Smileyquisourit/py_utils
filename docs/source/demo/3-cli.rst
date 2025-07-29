============================
3 - A simple CLI application
============================

Now that we’ve completed the core module, we can start developing a command-line interface (CLI) for the 
application.

We’ve already defined an entry point in the *pyproject.toml* file, pointing to the :func:`main` function 
in *WordleSolver/__main__.py*. This means that running the module with :code:`python -m WordleSolver` will 
trigger the same entry point. We'll stick with this approach and build a cli sub-module to contain the CLI 
logic, while *__main__.py* will handle user-provided arguments and launch the appropriate process.

To handle command-line arguments, we’ll use Python’s built-in :mod:`argparse` module. We'll define two 
subparsers:

- One for database-related operations
- One for search operations

Following this logic, we’ll also split the code within the cli sub-module into separate scripts, plus an additional 
one to define the main argument parser. After adding the cli sub-module, your project structure should look like
this: ::

    ├── demo/
    │   ├── pyproject.toml
    │   ├── WordleSolver/
    │   │   ├── cli/
    │   │   │   ├── parser.py
    │   │   │   ├── database.py
    │   │   │   ├── search.py
    │   │   │   └── __init__.py
    │   │   ├── core/
    │   │   │   ├── database.py
    │   │   │   ├── search.py
    │   │   │   └── __init__.py
    │   │   ├── __init__.py
    │   │   └── __main__.py


Defining the Parser
-------------------

The first step is to define the main :mod:`argparse` parser that will expose the available commands to the user. We’ll 
do this in the *WordleSolver/cli/parser.py* script. We’ll add one common argument to the parser — the log level — and 
define two subparsers: one for database-related operations, and one for search operations.

The common argument (:code:`--log-level`) allows the user to control the verbosity of log messages. We’ll use the 
:meth:`factory` method of the :class:`LogLevel` class to convert the input into the appropriate enum value.

.. code-block:: python

    import argparse

    from py_utils.Logueur.log_level import LogLevel

    parser = argparse.ArgumentParser(
        prog = 'WordleSolver',
        description = "A simple cli application to solve the NY Times Wordle game."
    )
    subparsers = parser.add_subparsers(
        title = "actions",
        dest='cmd',
        required = True
    )

    parser.add_argument(
        "-ll", "--log-level", 
        help="The severity level of the log messages. Default to 'INFO'",
        type=LogLevel.factory,
        default=LogLevel.INFO
    )

    # Database Parser
    # ===============

    db_parser = subparsers.add_parser("db", help="Database related operations.")


    # Search Parser
    # =============

    search_parser = subparsers.add_parser("search", help="Search related operations.")

To test this base structure, we’ll modify the *main.py* script:

.. code-block:: python

    from .cli.parser import parser

    def main():

        args = parser.parse_args()

        print("Hello wordle !")
        print(f"-ll {args.log_level} as type {type(args.log_level)}")


    if __name__ == "__main__":
        main()

Now, if you run the module with the :code:`-h` flag, you should see a help message listing the two available actions: *db* 
and *search*. You can also try out different log levels using the :code:`-ll` option, like :code:`debug` or :code:`ERROR`.
The factory method of the :class:`LogLevel` should word with *debug*, *info*, *warning*, *error* and *fatal*, and is insensible
to case.

If everything is working correctly at this stage, you're ready to start implementing the actual functionality for each CLI command!


Database operations
-------------------

We will provide two actions related to database management:

1. Initialize the database (i.e., create it),
2. Update the database with a list of words retrieved from a URL.

Both actions will be handled through the same subparser. To create the database, we only need the filename. To update the database, we 
need both the filename and a URL pointing to a list of words. If the :code:`--url` is used during initialization, the database will be 
automatically populated after creation.

Add the following to the *parser.py* file:

.. code-block:: python

    ...

    # Database Parser
    # ===============

    db_parser = subparsers.add_parser("db", help="Database related operations.")

    db_parser.add_argument(
        "action", choices=["init","update"],
        help="The action to perfom. 'init' will create the database, and 'update' will fill it with words."
    )
    db_parser.add_argument(
        "file",
        help="The file name of the database."
    )
    db_parser.add_argument(
        "-u","--url",
        help="The url into wich the words are defined. If used with the 'init' command, it will be used to automagically " + \
        "update the database. This argument is mendatory when updating the database."
    )

    ...

Now we’ll implement the actual logic for creating or updating the database in the *WordleSolver/cli/database.py* script:

.. code-block:: python

    import os
    import tempfile
    import urllib.request

    from py_utils.Logueur import Logueur

    from ..core.database import WordleDatabase


    def main_db(log:Logueur, action:str, filename:str, url:str=None):

        log.debug(
            "Starting database action using the following args:\n" + \
            f"  - action = {action}\n"+ \
            f"  - filename = {filename}\n"+ \
            f"  - url = {url}\n"
        )

        if action == "init":
            log.info(f"Creating the database using '{filename}' as the filename.")
            db = WordleDatabase.create(filename)
        else:
            db = WordleDatabase(filename)

        if url:
            log.info(f"Updating the database using the following url: {url}")

            with tempfile.NamedTemporaryFile('w+') as tmp_file:

                log.debug(f"Retrieving words in temporary file {tmp_file.name}")
                urllib.request.urlretrieve(url,tmp_file.name)

                log.debug(f"{os.path.getsize(tmp_file.name)} bytes downloaded, starting to parse it.")
                old_size = len(db)
                db.update(tmp_file)

                log.info(f"Added {len(db) - old_size} words in the database !")
                log.info(f"The database have now {len(db)} words.")

            pass

        if action == 'update' and not url:
            log.error("The url option is mandatory when updating the db ! Whithout it, no action are taken.")

The last thing to do is to Update the *__main__.py* file to call :code:`main_db()` when the appropriate subcommand is selected. Note that 
we also initialize the logger here:

.. code-block:: python

    from py_utils.Logueur import ConsoleLogueurFactory

    from .cli.parser import parser
    from .cli.database import main_db

    def main():

        # Parse arg and create logueur
        args = parser.parse_args()
        log = ConsoleLogueurFactory(level=args.log_level)

        log.info("Hello Wordle !!\n")
        if args.cmd == "db":
            main_db(log,args.action,args.file,args.url)

You can now create a database using a real word list from the following URL: ::

    https://raw.githubusercontent.com/tabatkins/wordle-list/main/words

You can try the following command:

.. code-block:: bash

    python3 -m WordleSolver -ll debug db init words.db -u "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words" 

You should see the different log output that tell you exactly what's going on ! The only down side is 
that the output isn't really user-friendly. Fortunately, we can modify the default format of the messages
directly in the :class:`Logueur` instance !

We just need to add the following line after the creation of the :class:`Logueur`:

.. code-block:: python

    ...
    log = ConsoleLogueurFactory(level=args.log_level)
    log._messageFormat = "{body}\n"

Now, if you try to rerun the last command (don't forget to delete the words.db file first), you should see
a more user-friendly output for the messages logged using the :class:`Logueur`. By running the same command
but with the :code:`INFO` level (the default level), you should only see a user-friendly output !


Search Operation
----------------

If you remember correctly from the implementation of the search functionalities, we have implemented a
:func:`oneshot_search` to conduct a search. We will use this function for the CLI. 

To implement the search functionality, we will follow the exact same step as for the database operations.
First we need to add the :code:`search_parser` subparser in the *parser.py* script:

.. code-block:: python

    # Search Parser
    # =============
    
    search_parser = subparsers.add_parser("search", help="Search related operations.")
    
    search_parser.add_argument(
        "database",
        help="The database in wich to search."
    )
    search_parser.add_argument(
        "word",
        help="The word to search. Replace the letter you don't know by '*'"
    )
    search_parser.add_argument(
        "-c", "--contain",
        help="Letter that is in the word, but you only know the position where it isn't. " + \
            "Give in the following format: 'l [1,2] m [2,3,5]', where l and m are the letter and the number in parentheses are the position to exclude.",
        default="", nargs="*"
    )
    search_parser.add_argument(
        "-v","--invert-match",
        help="Letters to exclude.",
        default="", dest="exclude"
    )
    search_parser.add_argument(
        "-n", "--nb-word",
        help="The number of word to return.",
        default=15, type=int, dest="n_word" 
    )
