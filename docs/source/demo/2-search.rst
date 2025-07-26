==========
2 - Search
==========

Now that we have a database to search in, we can implement the search functionality. The first step
is to create the *WordleSolver/core/search.py* script, where we will implement this functionality. Then, we will
define two classes: one to represent the *target* of a search, and another to represent a *search* for a word.

Once you’ve created the *search.py* script, your project should look something like this: ::

    ├── demo/
    │   ├── pyproject.toml
    │   ├── WordleSolver/
    │   │   ├── core/
    │   │   │   ├── database.py
    │   │   │   ├── search.py
    │   │   │   └── __init__.py
    │   │   ├── __init__.py
    │   │   ├── __main__.py


Target of a search
------------------

In Wordle, you can get three different kinds of clues. The first is a *green letter*, which indicates that the letter
is correctly placed in the word. The second kind is a *yellow letter*, which means that the letter is in the word but
not in that position. The last is a *grey letter*, which means that the letter is not in the word at all.

The :class:`WordleTarget` class should contain all this information. It will have:

- a list of five values for the green letters,
- a dictionary for the yellow letters, and
- another list for the grey letters.

We will declare the green letters as a list of 5 characters and provide five property decorators
to access each of the five letters individually. The yellow letters dictionary will use the letter as the key
and a list of positions where the letter is not as the value. Finally, the grey letters list will contain all letters that
isn't in the word.

In the constructor, we will initialize the green letters list as a list of None values, except where a letter is provided.
We can do this by using optional arguments in the constructor:

.. code-block:: python

    class WordleTarget():

        green_letters : list
        yellow_letters: dict
        grey_letters  : list

        @property
        def first(self) -> str:
            return self.green_letters[0]
        @first.setter
        def first(self,letter:str):
            self.green_letters[0] = letter

        @property
        def second(self) -> str:
            return self.green_letters[1]
        @second.setter
        def second(self,letter:str):
            self.green_letters[1] = letter

        @property
        def third(self) -> str:
            return self.green_letters[2]
        @third.setter
        def third(self,letter:str):
            self.green_letters[2] = letter

        @property
        def fourth(self) -> str:
            return self.green_letters[3]
        @fourth.setter
        def fourth(self,letter:str):
            self.green_letters[3] = letter

        @property
        def fifth(self) -> str:
            return self.green_letters[4]
        @fifth.setter
        def fifth(self,letter:str):
            self.green_letters[4] = letter

        def __init__(self, first:str=None, second:str=None, third:str=None, fourth:str=None, fifth:str=None):

            self.green_letters = [first,second,third,fourth,fifth]
            self.yellow_letters = dict()
            self.grey_letters = list()

We will also add the :code:`__repr__()` dunder method to provide a clear string representation of the target.
It will display the word by replacing unknown letters with the :code:`'*'` character, then append the dictionary
of yellow letters (prefixed with :code:`'-c'`) and the list of grey letters (prefixed with :code:`'-v'`):

.. code-block:: python

    class WordleTarget():

        ...

        def __repr__(self) -> str:
            word = ''.join([letter if letter else '*' for letter in self.green_letters])
            return f"'{word}' -c {self.yellow_letters} -v {self.grey_letters}"


Initialisation of the search
----------------------------

Now that we have defined what to search for, we can start implementing the search itself. The search will consist of 
removing words from a table according to the clues provided by Wordle. To avoid having to rebuild the entire database 
each time we run a search, we will use a temporary table.

Each time we refine the temporary table, we will:

1. Delete all words that do not have the known green letters in the correct positions.
2. Delete all words that do not contain the required yellow letters at all, or that contain them in an incorrect position.
3. Finally, delete all words that contain any grey letters.

The :class:`WordleSearch` will have 3 main attributes:

- A log function, similar to the one defined in the :class:`WordleDatabase`,
- A :class:`WordleDatabase` instance in which to search.
- A string containing the name of the temporary table where the search is conducted.

.. code-block:: python

    from py_utils.Logueur import Logueur
    from .database import WordleDatabase

    class WordleTarget():
        ...

    class WordleSearch():

        def __init__(self,database:WordleDatabase):

            # Initalize instance
            self._log = Logueur.get_logging_func()
            self._db = database
            self._tmp_table_name = None

As you can see, :code:`_tmp_table_name` is initialized with :code:`None`. We’ll explain why shortly, but for now let’s define the 
destructor for the :class:`WordleSearch`. Since we might create a temporary table during the search, we must be sure to remove it 
at the end! 

This is easily done:

.. code-block:: python

    class WordleSearch():

        ...

        def clean(self):
            if self._tmp_table_name:
                self._log("DEBUG",f"Found temporary table '{self._tmp_table_name}'. Deleting it.")

                try:
                    self._db.execute(f"DROP TABLE {self._tmp_table_name}",tuple())
                    self._db.commit()
                    self._tmp_table_name = None
                except Exception as e:
                    self._log("WARNING",f"There was an error while trying to delete the temporary table {self._tmp_table_name}:\n{e}")

        def __del__(self):
            self._log("DEBUG",'Deleting search.')
            self.clean()
            

.. note::
    An error may occure when trying to execute some commands on a database with it's connection already closed. Such a situation can 
    occure when Python destroy all remaining objects and start by destroying the WordleDatabase instance first. This is why you should
    call :meth:`clean` at the end of you script !


Before moving on to implementing the search logic, we will add the same two dunder methods that we implemented in the :class:`WordleDatabase`: 
the :meth:`__len__` and :meth:`__contains__` methods. The logic will be the same, except that they will operate on the temporary table instead 
of the words table. If there is no temporary table yet, it means we haven’t started the search, so every word is still possible. In this case, 
the methods will fall back to the corresponding methods in the :class:`WordleDatabase`.

.. code-block:: python

    class WordleSearch():

        ...

        def __len__(self) -> int:

            if self._tmp_table_name:
                self._db.execute(f"SELECT COUNT() FROM {self._tmp_table_name}",tuple())
                _len = self._db.fetch('one')
                return _len[0] if _len else 0

            return len(self._db)

        def __contains__(self,word:str) -> bool:

            if self._tmp_table_name:
                self._db.execute(f"SELECT if FROM {self._tmp_table_name} WHERE word = (?)",(word.strip().lower(),))
                return True if self._db.fetch('one') else False

            return self._db.__contains__(word)


Conducting a search
-------------------

As mentioned earlier, a search consists of removing words that don't satisfy certain conditions.
It's best to maintain a list of all possible words somewhere so that we don’t have to rebuild the entire database for each new search.
For this reason, we’ll create a temporary table where words can be removed, knowing they are still preserved elsewhere in the database.

To simplify the *user interface*, we will implement a single method: :meth:`search` which performs the filtering in three steps:

1. Remove from the table all words that don’t match the *green letters* positions.
2. Remove all words that don’t satisfy the *yellow letters* constraints.
3. Remove all words that contain any of the *grey letters*.

Each of these steps will be implemented in its own helper method, and the :meth:`search` method will simply call them in order. This 
allows us to expose a single, unified search method that takes a :class:`WordleTarget` instance, while still keeping the filtering logic 
clean and modular.

Once the filtering is complete, we’ll return a list of words that match the constraints. We let the user decide how many words should be 
returned — with the option to return all matching words if the specified number is less than or equal to 0.

.. code-block:: python

    class WordleSearch():

        ...

        def search(self, target:WordleTarget, nb_words:int = -1):

            # Green pass
            # TODO

            # Yellow pass
            # TODO

            # Grey pass
            # TODO

            # Process return
            if nb_words <= 0:
                nb_words = self.__len__()
            self._db.execute(f"SELECT word FROM {self._tmp_table_name} LIMIT ?", (nb_words,))

            return tuple( word[0] for word in self._db.fetch('all') )

.. note::
    The :code:`fetchall` method used by the :code:`fetch('all')` method returns a list of tuples, each containing a single word.
    Since we’re only interested in the word itself, we extract the first element from each tuple before returning.


First pass
~~~~~~~~~~

.. need to explain how we can create the table if it's the first pass or delete
.. from the tmp table when it's not.

The logic of the first pass is quite straight forward: if a word doesn't have a green letter at the correct position,
we delete it. But before deleting the words, we need to have them in the temporary table. One approch is that we can 
just copy the *words* table and then start the first pass, but this is kind of a waste of ressources because we will
copy a lot of words only to keep a few of them. The second approch is to create the temporary table by copying only
the words that respect the *green letters* condition.

We will implement a :meth:`_green_pass` method to implement the logic of the first pass. We will start by checking if
the :code:`_tmp_table_name` attribut contain something, and if not we will create the temporary table and save it's name.
The name will be created using the :mod:`uuid` module of python, so don't forget to import it !

.. code-block:: python

    class WordleSearch():

        ...

        def search(self, target:WordleTarget, nb_words:int = -1):
            
            ...

            # Green pass
            self._green_pass(target.green_letters)
            if self.__len__() == 0:
                self._log("DEBUG","No word found after first pass (green letters), returning early")
                return tuple()
            self._log("DEBUG", f"Found {self.__len__()} words after first pass (green letters).")

            ...

        def _green_pass(self, letters:list[str]):

            # Parse letters:
            l_enum = [(i,letter) for i,letter in enumerate(letters,start=1) if letter]
    
            # SQL cmd if there is no temporary table
            if not self._tmp_table_name:
                self._tmp_table_name = f"tmpSearch_{uuid.uuid4().hex}"
                self._log("DEBUG",f"No temporary table found, will create one with the name '{self._tmp_table_name}' for the green pass")
    
                sql_cmd = f"CREATE TABLE {self._tmp_table_name} AS SELECT * FROM words"
                sql_arg = tuple()
    
                if l_enum:
                    l_pos, l_char = zip(*l_enum)
                    sql_cmd += " WHERE " + " AND ".join( [f"letter{i}_id= ?" for i in l_pos] )
                    sql_arg = tuple( self._db.get_letter_id(l) for l in l_char )   
    
            # SQL cmd if there is already a temporary table
            else: 
                self._log("DEBUG", f"Found temporary table '{self._tmp_table_name}', using it for the green pass.")
    
                if not l_enum:
                    # No green letters, so we can return early
                    return
                
                l_pos, l_char = zip(*l_enum)
    
                sql_cmd = f"DELETE FROM {self._tmp_table_name} WHERE NOT (" + " OR ".join( [f"letter{i}_id= ?" for i in l_pos] ) + ")"
                sql_arg = tuple( self._db.get_letter_id(l) for l in l_char ) 
    
            # Execute SQL command
            self._db.execute(sql_cmd,sql_arg)
            self._db.commit()

Second pass
~~~~~~~~~~~

.. To be review. Add log error and return early when there is no temporary table !

That being said, there is a small problem with this blunt logic. If you have a green letter at the first position, lets say the
`'e'`, you can also have it at an other place like in the word `'eager'`. In this case, when doing the second pass (with the yellow
letters), you can't only check that there is an `'e'` in the word, as this condition will always be true because of the first letter.
We need a way to check that if a letter is in the green letters list and in the yellow letters dictionary, it need to be at least
2 of this letter in the word.

Third pass
~~~~~~~~~~

.. To be review. Add log error and return early when there is no temporary table !

We have the same problem with the green and grey letters list. Let's say that we are now looking for the `'earth'` word, and that 
we know that we only have the `'e'` letter at the first position and at no other. If we specified the `'e'` in the green and the
grey letters list, the first pass will add every word that start with `'e'`, but the third pass will delete all words that contain
it ! Like for the second pass, we need a way to delete the words where there is 2 or more grey letter in the case where the grey
letter is also in the green letter, or more if there is more than twice the same letter in the word.


One shot search
---------------

.. 1 section to implement a one shot search function

