# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# DEMO - Core logic of the database.
# ---------------------------------------------------------
# demo/WordleSolver/core/database.py

import os
import sqlite3 as sql
from typing import Iterable

from py_utils.Logueur import Logueur

_ALL_LETTERS = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')


class WordleDatabase():

    def __init__(self, filename:str):
        """ A class representing a words database. """
    
        # Initialise log
        self._log = Logueur.get_loggingFunc()
        
        # Check file
        if not os.path.exists(filename):
            self._log("FATAL", f"The database file '{filename}' wasn't found !")
            raise FileNotFoundError(f"The database file '{filename}' wasn't found !")
        self._file = filename
    
        # Open database
        self._connection = sql.connect(self._file)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._cursor = self._connection.cursor()

        # Check foreign keys
        self._cursor.execute("PRAGMA foreign_keys;")
        if not (pragma_key := self._cursor.fetchone()) or pragma_key[0] == 0:
            self._log("WARNING",
                    "The 'foreign_keys' option isn't activated or wasn't found in the database !\n" + \
                    "The application could malfunction or generate inaccurate answers in the future."
                )
            
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
    
    def __len__(self) -> int:
        self._cursor.execute("SELECT COUNT() FROM words")
        _len = self._cursor.fetchone()

        return _len[0] if _len else 0
    
    def __contains__(self,word:str) -> bool:
        self._cursor.execute("SELECT id FROM words WHERE word = (?)",(word.strip().lower(),))

        return True if self._cursor.fetchone() else False

    @classmethod
    def create(cls, filename:str):
        """ Create a database and construct the instance of WordleDatabase.

        Create the database and populate it using the given iterable, then instantiate the 
        WordleDatabase instance.
        
        :param file str: The path to the database file.


        :return: The WordleDatabase linking to the created database.
        :rtype: WordleDatabase
        """

        # Get logging function
        _log = Logueur.get_loggingFunc()

        # Check filename
        if os.path.exists(filename):
            _log("FATAL",f"The file '{filename}' already exist, aborting.")
            raise FileExistsError(f"The file '{filename}' already exist, aborting.")
        _log("DEBUG",f"Creating database '{filename}' !")
        
        # Create the database
        connection = sql.connect(filename)
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.cursor()

        # Create and populate the letters table 
        cursor.execute(""" CREATE TABLE letters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                letter CHAR(1) UNIQUE NOT NULL
                );""")
        for letter in _ALL_LETTERS:
            cursor.execute("INSERT INTO letters (letter) VALUES (?);",(letter,))

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


    def get_letter_id(self,letter:str):
        """ Get letter id. """

        self._cursor.execute("SELECT id FROM letters WHERE letter = (?);", (letter.lower()))
        id = self._cursor.fetchone()

        return id[0] if id else None

    def update(self, words:Iterable[str]):
        """ Update the database with an iterable of words. """

        n_word = 0

        for word in words:

            word = word.strip().lower()

            # Check size
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

