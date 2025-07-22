============
1 - Database
============

Presentation
------------

The first fundamental building block of this application is its database.  
Since Wordle uses a large list of words, we need an efficient way to store and filter them using various criteria.  
For this purpose, we will use an SQLite3 database with two tables:

- The first table contains the 26 letters of the English alphabet, each associated with a unique ID.
- The second table stores the words. Each word entry includes:

  - An `id` (the primary key of the table)
  - The word itself, marked as `UNIQUE` to prevent duplicates
  - Five IDs linking each letter of the word to the corresponding letter ID in the first table

Using IDs to represent letters is slightly more complex than simply storing the characters directly.
However, normalizing the tables this way — by using `INTEGER` keys instead of text — makes the database more robust and consistent.
For the same reason, we can declare the IDs linking each letter of the word to the ID of the letter as a FOREIGN KEY.   
This adds a small amount of complexity but should have no significant impact on performance for a database of this size, and will 
allow better integration of future improvements.

.. image:: /_static/demo/database-1.png
   :alt: The database scheme
   :scale: 100%
   :align: center

In this example, we won’t go too deeply into database architecture and programming, as that is not the main goal of this demonstration.
The following command creates the *letters* table:

.. code-block:: sql

    CREATE TABLE letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        letter CHAR(1) UNIQUE NOT NULL
    );

For the *words* table, the command is slightly more complex due to the use of `FOREIGN KEY`:

.. code-block:: sql

    CREATE TABLE words (
        id INTEGER PRIMARY KEY,
        word CHAR(5) UNIQUE NOT NULL,
        letter1_id INTEGER NOT NULL,
        letter2_id INTEGER NOT NULL,
        letter3_id INTEGER NOT NULL,
        letter4_id INTEGER NOT NULL,
        letter5_id INTEGER NOT NULL,
        FOREIGN KEY (letter1_id) REFERENCES letters(id),
        FOREIGN KEY (letter2_id) REFERENCES letters(id),
        FOREIGN KEY (letter3_id) REFERENCES letters(id),
        FOREIGN KEY (letter4_id) REFERENCES letters(id),
        FOREIGN KEY (letter5_id) REFERENCES letters(id)
    );

With Python’s :mod:`sqlite3` module, foreign keys are not enforced by default, so
you must explicitly enable them. Do this immediately after opening the database:

.. code-block:: sql

    PRAGMA foreign_keys = ON

In Python, you can do this with the following instructions:

.. code-block:: python

    # Import the module
    import sqlite3 as sql

    # Open the database
    connection = sql.connect(DB_FILE)
    connection.execute('PRAGMA foreign_keys = ON')

    # Get the cursor for normal operations
    cursor = connection.cursor()

Before continuing to the creation of the database, we will need to create the *WordleSolver/core* directory,
with two files: an *__init__.py* and a *database.py* file. As before, the *__init__.py* can be empty, it's only
here so that python consider the *core* directory as a package. The *database.py* script will contain the 
:class:`WordleDatabase` class. ::

    ├── demo/
    │   ├── pyproject.toml
    │   ├── WordleSolver/
    │   │   ├── core/
    │   │   │   ├── database.py
    │   │   │   └── __init__.py
    │   │   ├── __init__.py
    │   │   ├── __main__.py


Creating the database
---------------------

Before implementing the :class:`WordleDatabase`, we need to decide which part of the code is responsible
for creating the database, and which part interacts with it.
I believe the creation logic should not be handled by the constructor of the class that interacts with the database.
The constructor should open an existing database, not create one.
However, since the two tasks are closely related, the creation logic should still belong to the same class, but as a `classmethod`.

We will also separate the creation logic from the logic that populates the database,
since the populate logic can be reused to update the database later.  
Our `create` `classmethod` will only create the database file and the two tables, and populate only the *letters* table,
since it is fixed (only 26 letters).  
So we can hardcode this set in our module. Let’s define it at the start of the *core/database.py* script, and import the 
:mod:`sqlite3` module:

.. code-block:: python

    import sqlite3 as sql

    _ALL_LETTERS = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')

Next, we implement the *classmethod* responsible for creating the database.
For now, we will ignore the constructor and focus only on this creation method.

.. code-block:: python

    class WordleDatabase():

        def __init__(self, *args, **kwargs):
            pass

        @classmethod
        def create(cls, filename:str):
            """ Create a database. """
            pass

Before doing anything, we need a way to log what we’re doing. Since this is a module and not the final application,
we don’t know if there’s an existing logging system or what its logging level is.
For this, the :class:`~py_utils.logueur.Logueur` class provides a class method to get a logging function
that either uses the application’s logging system or defaults to printing messages to the console, filtered at the `WARNING` level.
We will soon implement the logging system for the *CLI* application, but for now we’ll use the default logger.
Don’t forget to import the :class:`~py_utils.logueur.Logueur` class!

.. code-block:: python

    from py_utils.Logueur import Logueur

    ...

        @classmethod
        def create(cls, filename:str):
            """ Create a database. """
            
            # Get logging function
            _log = Logueur.get_loggingFunc()

We are now ready to log our first message ! We will check if the file already exists using the :mod:`os` module
and then, depending on the result, log an appropriate message.
If the file exists, log a `FATAL` message and raise an error — we don’t want to overwrite an existing file.
Otherwise, log a `DEBUG` message to indicate that we are creating the database.

.. code-block:: python

    import os
    import sqlite3 as sql

    from py_utils.Logueur import Logueur

    ...

        @classmethod
        def create(cls, filename:str):
            """ Create a database. """
            
            # Get logging function
            _log = Logueur.get_loggingFunc()

            # Check filename
            if os.path.exists(filename):
                _log("FATAL",f"The file '{filename}' already exist, aborting.")
                raise FileExistsError(f"The file '{filename}' already exist, aborting.")
            _log("DEBUG",f"Creating database '{filename}' !")

We can now create the database. For this, we just need to open a connection and the :mod:`sqlite3` will create the
associated file. Once the database is opened, we can create the letters table and populate it. This is 
quite straigth forward:

.. code-block:: python

    ...

            # Create the database
            connection = sql.connect(filename)
            cursor = connection.cursor()

            # Create and populate the letters table
            cursor.execute(""" CREATE TABLE letters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                letter CHAR(1) UNIQUE NOT NULL
                );""")
            for letter in _ALL_LETTERS:
                cursor.execute("INSERT INTO letters (letter) VALUES (?);", (letter,))

Then, we just need to create the words table without populating it, commit our change to the database, and
close it. As the newly created database will certainly be used right after it's creation, we can return it
to the user by calling it's :meth:`__init__` method:

.. code-block:: python

    ...

            # Create the words table
            cursor.execute(""" CREATE TABLE words (
                id INTEGER PRIMARY KEY,
                word CHAR(5) UNIQUE NOT NULL,
                letter1_id INTEGER NOT NULL,
                letter2_id INTEGER NOT NULL,
                letter3_id INTEGER NOT NULL,
                letter4_id INTEGER NOT NULL,
                letter5_id INTEGER NOT NULL,
                FOREIGN KEY (letter1_id) REFERENCES letters(id),
                FOREIGN KEY (letter2_id) REFERENCES letters(id),
                FOREIGN KEY (letter3_id) REFERENCES letters(id),
                FOREIGN KEY (letter4_id) REFERENCES letters(id),
                FOREIGN KEY (letter5_id) REFERENCES letters(id)
                ); """)

            # Commit and close database
            connection.commit()
            connection.close()

            return cls(filename)

We can test our :meth:`create` method by modifying the *WordleSolver/__main__.py* file to execute it. For
this, we will first need to import our module, and then simply call our method in the :func:`main` function:

.. code-block:: python

    from .core.database import WordleDatabase

    def main():

        db = WordleDatabase.create('words.db')

The first time you run the script (ie by calling the module or the *cli* command), you shouldn't see anything
on the terminal, as the only message that we log is a `'DEBUG'` message, and the default logueur filtrate the 
messages with the `'WARNING'` level. You should only see a new *words.db* file in your explorer. But if you
run the demo a second time, you should see the :class:`FileExistsError` and the following message just before::

    [FATAL] database.WordleDatabase.create :: The file 'words.db' already exist, aborting.

If you want to see the `"DEBUG"` message, you need to define a :class:`Logueur` instance with a `"DEBUG"`
level in the *__main__.py* script. You can do so with the :func:`~py_utils/Logueur/ConsoleLogueurFactory`
quite simply:

.. code-block:: python

    from py_utils.Logueur import ConsoleLogueurFactory

    from .core.database import WordleDatabase

    def main():

        log = ConsoleLogueurFactory("DEBUG")
        db = WordleDatabase.create('words.db')

You can then re-run the application to see it, and see the different option of the 
:func:`~py_utils/Logueur/ConsoleLogueurFactory` function. Don't forget to delete the *words.db* before !


Initialisation of the :class:`WordleDatabase`
---------------------------------------------

Now that we have created a database, we can start to implement our :class:`WordleDatabase`. We can implement
the constructor, that we ignored the first time, and start by creating a `_log` attribute:

.. code-block:: python

    ...

    class WordleDatabase():

        def __init__(self, filename:str):
            """ A class representing a words database. """
    
            # Initialise log
            self._log = Logueur.get_loggingFunc()


The first thing to do is to check the file of the database. For that, we can use the :mod:`os.path` module,
and raise an error if the file isn't found. Once this check is passed, we can open the database and activate
the foreign keys.

.. code-block:: python

        def __init__(self, filename:str):
            """ A class representing a words database. """

            ...

            # Check the file
            if not os.path.exists(filename):
                self._log("FATAL", f"The database file '{filename}' wasn't found !")
                raise FileNotFoundError(f"The database file '{filename}' wasn't found !")
            self._file = filename
    
            # Open the database
            self._connection = sql.connect(self._file)
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._cursor = self._connection.cursor()

We will rely on the `FOREIGN KEY` to ensure the coherence of our data, so it's a good idea to check
now that the `foreign_keys` option is correctly activated. If the option isn't activated, it will not 
break immediatly our application, but it can cause it to malfunction in the future, so we can log a 
warning:

.. code-block:: python

        def __init__(self, filename:str):
            """ A class representing a words database. """

            ...

            # Check foreign keys
            self._cursor.execute("PRAGMA foreign_keys;")
            if not (pragma_key := self._cursor.fetchone()) or pragma_key[0] == 0:
                self._log("WARNING",
                        "The 'foreign_keys' option isn't activated or wasn't found in the database !\n" + \
                        "The application could malfunction or generate inaccurate answers in the future."
                    )

As we open the database in the constructor, we will need to close it in the destructor to be sure to
free the associated ressources. If there is still a pending transaction when closing the database, ie
a *execute* command that isn't *commited*, we will log a warning and *rollback* the transaction, then
close the database properly.

.. code-block:: python

    class WordleDatabase():

        ...

        def __del__(self):
            """ Destructor. """

            if self._connection.in_transaction:
                self._log("WARNING",
                    f"There is still a pending transaction when closing the database,\n" + \
                    f"the last change will be ignored."
                )
                self._connection.rollback()

            self._cursor.close()
            self._connection.close()

You can try different scenario in the :func:`main()` function of the *WordleSolver/__main__.py* script to see the
logs in action. Don't hesitate to modify the :class:`WordleDatabase` by commenting certain lines out, like the 24
of *database.py*, to simulate the case where the foreign keys wern't activated !

.. note::
    You can also change the :func:`main()` function to use the constructor of the database rather than the 
    :meth:`WordleDatabase.create()` ! 


Basics Functionalities of the database
--------------------------------------

Before implementing the method to update and populate the database, we will implement a helper method to
map a letter to it's id, and two handy dunder methods. To map a letter to it's id, we just need to use the
following sql command:

.. code-block:: sql

    SELECT id FROM letters WHERE letter = (?);

Where the `(?)` will be replaced by the wanted letter. As we only added lower characters into the *letters*
table, we can lower the given letter before asking the database:

.. code-block:: python

    class WordleDatabase():

        ...

        def get_letter_id(self,letter:str):
            """ Get letter id. """

            self._cursor.execute("SELECT id FROM letters WHERE letter = (?);", (letter.lower()))
            id = self._cursor.fetchone()

            return id[0] if id else None

The two dunder methods that may comme in handy in the future are the :meth:`__len__` and :meth:`__contain__`
methods. The first one will implement how we can compute the lenght of the :class:`WordleDatabase`, and the
second one will implement what should return the following python statement:

.. code-block:: python

    >> database = WordleDatabase(filename)
    >> some_variable in database
    # return True if some_variable is in the database

For the lenght of the database, we will consider the number of words in the *words* table, and the second
will check if a word is in the *words* database. The implementation for those two methods are the following:

.. code-block:: python

    ... 
    class WordleDatabase():

        ...

        def __len__(self) -> int:
            self._cursor.execute("SELECT COUNT() FROM words")
            _len = self._cursor.fetchone()

            return _len[0] if _len else 0

        def __contains__(self,word:str) -> bool:
            self._cursor.execute("SELECT id FROM words WHERE word = (?)",(word.lower(),))

            return True if self._cursor.fetchone() else False

You can test those 2 methods by calling them in the *__main__.py* script:

.. code-block:: python

    def main():

        db = WordleDatabase('words.db')

        print(f"Lenght of the database: {len(db)}")
        print(f"Word 'stare' in database: {'stare' in db}")

.. note::
    The :func:`len` should only return 0 and the :code:`'stare' in db` should always return :code:`False`
    for now !

Main functionalities of the database
------------------------------------

Now that most of the methods that represent the database, we can start adding word to it. For
that, we will create an *update* method that will take a list of words, and try to append it to
the table.

For each word in the list, we will first strip it (remove blank caracter) and lower it. We will then
check the size of the word, and get the ids of each letter in the word. If there isn't 5 letters or
if one letter isn't found in the *letters* table, a warning will be logged and the word will be ignored.

.. note::
    To make thing more clear, we will use the :class:`Iterable` class of the :mod:`typing`
    for the type hint of the list of words, so we will need to import it.

.. code-block:: python

    from typing import Iterable

    ...

    class WordleDatabase():

        ...

        def update(self, words:Iterable[str]):
            """ Update the database with an iterable of words. """

            n_word = 0

            for word in words:

                word = word.strip().lower()

                # Check size
                if len(word) != 5:
                    self._log("WARNING", f"Found a word with {len(word)} letters to append to the database, ignoring it.")
                    continue

                # Get letters id
                ids = list()
                for letter in word:
                    if not (l_id := self.get_letter_id(letter)):
                        self._log("WARNING",f"An unknown letter was found: {letter}, ignoring the word '{word}'")
                        break
                    ids.append(l_id)
                if not len(ids) == 5:
                    continue

                # Add word in the database
                try:
                    self._cursor.execute(
                        "INSERT INTO words (word, letter1_id, letter2_id, letter3_id, letter4_id, letter5_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (word, ids[0], ids[1], ids[2], ids[3], ids[4])
                    )
                    n_word += 1
                except sql.IntegrityError as e:
                    self._log("WARNING",f"Error when trying to add word '{word}':\n{e}\nIgnoring it.")

            self._log("DEBUG", f"Added {n_word} words in the database !")
            self._connection.commit()

To test this :meth:`update()` method, we can define a list of words and try to add them into our database. To do so,
we can modify our *__main__.py* script in the following way:

.. code-block:: python

    def main():

        db = WordleDatabase('words.db')

        print(f"Lenght of the database: {len(db)}")
        print(f"Word 'stare' in database: {'stare' in db}")

        words_list = [
            "rossa",
            "jetty",
            "wizzo",
            "cuppa",
            "cohoe",
            "gurks",
            "squad",
            "beisa",
            "shrug",
            "stare"
        ]

        print("Updating the database...")
        db.update(words_list)

        print(f"Lenght of the database after update: {len(db)}")
        print(f"Word 'stare' in database after update: {'stare' in db}")



The last functionalities to implement is an interface to execute some sql commands on the database. There is multiple
complexe ways to do this in a safe maner, but this is not the goal of this example, so we will settle to a simpler 
*unsafe* method. We will simply expose a :meth:`execute` method that will take an SQL command and some parameters,
and some methods to fetch the values and commit the transaction. If there is an sql error while executing the commmand, 
we will catch it to log the error then re-throw it.

.. code-block:: python

    class WordleDatabase():

        ...

        def execute(self, sql_cmd:str, sql_parameters:tuple[any]):

            try:
                self._cursor.execute(sql_cmd,sql_parameters)
            except sql.Error as e:
                self._log("ERROR",
                    f"Error when trying to execute the following sql command:" + \
                    f"\ncmd='{sql_cmd}'; params={sql_parameters}\n{e.sqlite_errorname}[{e.sqlite_errorcode}] :: {e}"
                )
                raise e

        def fetch(self,cmd:str='one',size:int|None=1):
            if cmd == 'one':
                return self._cursor.fetchone()
            elif cmd == 'many':
                return self._cursor.fetchmany(size)
            elif cmd == 'all':
                return self._cursor.fetchall()

            else:
                self._log("ERROR",f"Unknwon fetch command '{cmd}', should be 'one', 'many', or 'all'.\nIgnoring the command.")

        def commit(self):
            self._connection.commit()