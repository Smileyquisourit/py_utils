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
For the same reason, we declare the IDs linking each letter of the word to the letter ID as `FOREIGN KEY`.   
This adds a small amount of complexity but should have no significant impact on performance for a database of this size and will allow 
better integration of future improvements.

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

For the *words* table, the command is slightly more complex due to the use of `FOREIGN KEY` constraints:

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
you must explicitly enable them immediately after opening the database:

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

Before continuing with the creation of the database, we need to create the *WordleSolver/core* directory,
with two files: an *__init__.py* and a *database.py* file. As before, the *__init__.py* can be empty; it only
exists so that Python treats the core directory as a package. The *database.py* script will contain the
:class:`WordleDatabase` class. ::

    ├── demo/
    │   ├── pyproject.toml
    │   ├── WordleSolver/
    │   │   ├── core/
    │   │   │   ├── database.py
    │   │   │   └── __init__.py
    │   │   ├── __init__.py
    │   │   └── __main__.py


Creating the database
---------------------

Before implementing the :class:`WordleDatabase`, we need to decide which part of the code is responsible
for creating the database and which part interacts with it.
The creation logic should not be handled by the constructor of the class that interacts with the database,
it should only open an existing database.
However, since these two tasks are closely related, the creation logic should still belong to the same class, 
but as a `classmethod`.

We will also separate the creation logic from the logic that populates the database,
since the populate logic can be reused later to update the database.  
Our :meth:`create` `classmethod` will only create the database file and the two tables, and populate only the 
*letters* table, since it is fixed (only 26 letters).  
So we can hardcode this set in our module. Let’s define it at the start of the *core/database.py* script, and 
import the :mod:`sqlite3` module:

.. code-block:: python

    import sqlite3 as sql

    _ALL_LETTERS = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')

Next, we implement the classmethod responsible for creating the database. For now, we will ignore the constructor 
and focus only on this creation method.

.. code-block:: python

    class WordleDatabase():

        def __init__(self, *args, **kwargs):
            pass

        @classmethod
        def create(cls, filename:str):
            """ Create a database. """
            pass

Before doing anything, we need a way to log what we’re doing. Since this is a module and not the final application,
we don’t know if there’s an existing logging system or what its logging level is. The :class:`~py_utils.logueur.Logueur` 
class provides a class method to get a logging function that either uses the application’s logging system or defaults 
to printing messages to the console, filtered at the `WARNING` level. We will soon implement the logging system for 
the *CLI* application, but for now we’ll use the default logger.

Don’t forget to import the :class:`~py_utils.logueur.Logueur` class!

.. code-block:: python

    from py_utils.Logueur import Logueur

    ...

        @classmethod
        def create(cls, filename:str):
            """ Create a database. """
            
            # Get logging function
            _log = Logueur.get_loggingFunc()

We are now ready to log our first message! We will check if the file already exists using the :mod:`os` module
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

Next, we create the database by opening a connection, :mod:`sqlite3` will create the file automatically.
Then we create the *letters* table and populate it. This is straightforward:

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

Then we create the *words* table, commit the changes, close the connection, and return an instance of the class:

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

To test our :meth:`create` method, modify the *WordleSolver/__main__.py* file as follows:

.. code-block:: python

    from .core.database import WordleDatabase

    def main():

        db = WordleDatabase.create('words.db')

The first time you run the script (via the module or the *cli* command), you shouldn’t see anything in the 
terminal, since the only message logged is `DEBUG` and the default logger filters for `WARNING`. You should, 
however, see the *words.db* file appear in your explorer. If you run it again, you’ll see a 
:class:`FileExistsError` and the following message:

    [FATAL] database.WordleDatabase.create :: The file 'words.db' already exist, aborting.

If you want to see the `DEBUG` message, you need to define a :class:`Logueur` instance with a `"DEBUG"`
level in the *__main__.py* script. You can do so with the :func:`~py_utils/Logueur/ConsoleLogueurFactory`
quite simply:

.. code-block:: python

    from py_utils.Logueur import ConsoleLogueurFactory

    from .core.database import WordleDatabase

    def main():

        log = ConsoleLogueurFactory("DEBUG")
        db = WordleDatabase.create('words.db')

Re-run the application to see the log in action — just remember to delete *words.db* first!


Initialisation of the :class:`WordleDatabase`
---------------------------------------------

Now that we have created the database, we can start implementing our :class:`WordleDatabase`. Let’s implement the 
constructor, which we skipped the first time, and start by creating a `_log` attribute:

.. code-block:: python

    ...

    class WordleDatabase():

        def __init__(self, filename:str):
            """ A class representing a words database. """
    
            # Initialise log
            self._log = Logueur.get_loggingFunc()


The first thing to do is check whether the database file exists. For that, we can use the :mod:`os.path` module 
and raise an error if the file isn’t found. Once this check passes, we can open the database and activate foreign 
keys:

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

We rely on `FOREIGN KEY` constraints to ensure the consistency of our data, so it’s a good idea to check that the 
foreign keys option is correctly activated. If it’s not, it won’t immediately break our application, but it could 
cause malfunctions in the future, so we’ll log a warning:

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

Since we open the database in the constructor, we need to close it in the destructor to free the associated resources. 
If there is still a pending transaction when closing the database (i.e., an *execute* command that hasn’t been committed), 
we’ll log a warning, rollback the transaction, and then close the database properly:

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

            self._log("DEBUG","Closing database.")
            self._cursor.close()
            self._connection.close()

You can try different scenarios in the :func:`main()` function of the *WordleSolver/__main__.py* script to see the logs in 
action. Don’t hesitate to modify the :class:`WordleDatabase` by commenting out certain lines, like line 24
of *database.py*, to simulate the case where foreign keys aren’t activated!

.. note::
    You can also change the :func:`main()` function to use the database constructor directly instead of the
    :meth:`WordleDatabase.create()` method! 


Basics Functionalities of the database
--------------------------------------

Before implementing methods to update and populate the database, we’ll implement a helper method to map a letter to its ID, 
and two useful dunder methods. To map a letter to its ID, we just need to use the following SQL command:

.. code-block:: sql

    SELECT id FROM letters WHERE letter = (?);

Since we only added lowercase characters to the letters table, we’ll convert the given letter to lowercase before querying 
the database:

.. code-block:: python

    class WordleDatabase():

        ...

        def get_letter_id(self,letter:str):
            """ Get letter id. """

            self._cursor.execute("SELECT id FROM letters WHERE letter = (?);", (letter.lower()))
            id = self._cursor.fetchone()

            return id[0] if id else None

The two dunder methods that may come in handy are :meth:`__len__` and :meth:`__contains__`. The first will compute the length 
of the :class:`WordleDatabase` class, and the second will implement what should happen with the following Python statement:

.. code-block:: python

    >> database = WordleDatabase(filename)
    >> some_variable in database
    # return True if some_variable is in the database

For the length, we’ll count the number of words in the *words* table. The :meth:`__contains__` method will check if a word exists 
in the *words* table. Here’s how to implement both:

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

You can test these methods in the *__main__.py* script:

.. code-block:: python

    def main():

        db = WordleDatabase('words.db')

        print(f"Lenght of the database: {len(db)}")
        print(f"Word 'stare' in database: {'stare' in db}")

.. note::
    The :func:`len` should only return 0 and the check :code:`'stare' in db` should always return :code:`False`
    for now !

Main functionalities of the database
------------------------------------

Now that we have most of the core methods, we can start adding words to the database. For that, we’ll create an 
*update* method that takes a list of words and tries to append them to the table.

For each word in the list, we’ll first strip it (remove blank characters) and convert it to lowercase. Then we’ll 
check its length and get the IDs of each letter. If the word doesn’t have 5 letters or contains an unknown letter, 
we’ll log a warning and ignore it.

.. note::
    To clarify things, we’ll use the :class:`Iterable` class from the :mod:`typing` module for the type hint, 
    so we’ll need to import it.

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
                if self.__contains__(word):
                    continue
                try:
                    self._cursor.execute(
                        "INSERT INTO words (word, letter1_id, letter2_id, letter3_id, letter4_id, letter5_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (word, ids[0], ids[1], ids[2], ids[3], ids[4])
                    )
                    n_word += 1
                except Exception as e:
                    self._log("WARNING",f"Error when trying to add word '{word}':\n{e}\nIgnoring it.")

            self._log("DEBUG", f"Added {n_word} words in the database !")
            self._connection.commit()

To test this :meth:`update()` method, define a list of words and try adding them to your database. 
Modify your *__main__.py* script like this:

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


The last functionality to implement is an interface to execute custom SQL commands. There are more robust ways to 
do this safely, but for this example, we’ll provide a simple (unsafe) method. We’ll expose an  :meth:`execute` 
method to take an SQL command and parameters, and add methods to fetch values and commit transactions. If there’s 
an SQL error while executing the command, we’ll log it and re-raise the error:

.. code-block:: python

    class WordleDatabase():

        ...

        def execute(self, sql_cmd:str, sql_parameters:tuple[any]):

            try:
                self._cursor.execute(sql_cmd,sql_parameters)
            except sql.Error as e:
                self._log("ERROR",
                    f"Error when trying to execute the following sql command:" + \
                    f"\ncmd='{sql_cmd}'; params={sql_parameters}\n[{type(e).__name__}] :: {e}"
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

You can test these by adding a word and fetching it afterwards. Try different words, or test an invalid one, like 
a six-letter word or a duplicate, to see the different log messages:

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

        db.execute(
            "INSERT INTO words (word, letter1_id, letter2_id, letter3_id, letter4_id, letter5_id) VALUES (?, ?, ?, ?, ?, ?);",
            (
                'float', 
                db.get_letter_id('f'), 
                db.get_letter_id('l'), 
                db.get_letter_id('o'),
                db.get_letter_id('a'),
                db.get_letter_id('t')
            )
        )
        db.execute(
            "SELECT word IN words WHERE letter1_id = (?);",
            (db.get_letter_id('f'),)
        )
        print(f"Word starting with 'f': {db.fetch('one')}")

What is next
------------

Now that we have implemented the interface for the database, we can start to implement the
search functionalities !
