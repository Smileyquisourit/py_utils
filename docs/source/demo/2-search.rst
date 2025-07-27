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
    │   │   └── __main__.py


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

The logic behind filtering yellow letters is fairly straightforward. From the yellow clues, we can delete two type of
words:

1. Words that don’t contain the required yellow letter.
2. Words that contain the yellow letter, but in the wrong position.

At first glance, this seems simple to implement using two queries:

- Delete words where the letter is missing: :code:`WHERE NOT (letter1_id = ? OR ... OR letter5_id = ?)`
- Delete words where the letter appears in a disallowed position: :code:`WHERE letter*_id = ?` (for each invalid position)

That being said, there is a small problem with this blunt logic: overlapping of green and yellow letters. Consider the 
case where a green letter `'e'` appears in the first position. A word like `'eager'` would match this constraint. If we
get a *yellow letter* clue on the fifth position, it means that we have 2 `'e'` in the word, one at the first position 
and an other that can be anywhere except on the first and fifth position. So if we apply the preceding logic, we will 
allow all word that have a `'e'`, like `'equal'`, but we are only interested by the words that posses 2 `'e'` !

To handle this properly, we need to count how many times a letter appears in a word and compare it to the number of times it 
appears in the green and yellow clues combined. If a letter appears *X* times in the green letters and is also in the yellow 
letters dictionary, then we must ensure that the word contains at least *X + 1* instances of that letter. To do that, we can 
use a more complex SQL command that adds up the number of matching positions for a given letter, then compares the total with 
a minimum threshold:

.. code-block:: sql

    DELETE FROM _tmp_table_name WHERE (
        (CASE WHEN letter1_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter2_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter3_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter4_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter5_id = ? THEN 1 ELSE 0 END) < ?
    )

We can now implement this logic accordingly in the `WordleSearch` class:

.. code-block:: python

    class WordleSearch():

        ...

        def search(self, target:WordleTarget, nb_words:int = -1):

            ...

            # Yellow pass
            self._yellow_pass(target.yellow_letters, target.green_letters)
            if self.__len__() == 0:
                self._log("DEBUG","No word found after second pass (yellow letters), returning early")
                return tuple()
            self._log("DEBUG", f"Found {self.__len__()} words after second pass (yellow letters).")

            ...

        def _yellow_pass(self, yellow_letters:dict, green_letters:list[str]):

            # Check tmp table
            if not self._tmp_table_name:
                self._log("ERROR", "No temporary table, aborting")
                return

            if len(yellow_letters.keys()) == 0:
                self._log("DEBUG", "No yellow letters, returning early.")
                return

            # Iterate over the yellow letters:
            for letter, poss in yellow_letters.items():

                # Filtrate based on occurence
                l_id = self._db.get_letter_id(letter)
                max_occ = 1 + sum( [1 for gl in green_letters if letter == gl] )
                self._db.execute(
                    f"DELETE FROM {self._tmp_table_name} WHERE (" + \
                        "(CASE WHEN letter1_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter2_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter3_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter4_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter5_id = ? THEN 1 ELSE 0 END) < ?" + \
                    ")",
                    (l_id, l_id, l_id, l_id, l_id, max_occ)
                )

                # Filtrate based on position
                for p in poss:
                    self._db.execute(f"DELETE FROM {self._tmp_table_name} WHERE letter{p}_id = ?", (l_id,))

                self._db.commit()

Third pass
~~~~~~~~~~


From the grey letter clues, we know which letters must not appear in the target word. So in theory, we could simply 
delete all words that contain any of those letters. However, we face the same kind of issue as we did in the yellow 
letter pass.

Let’s say we’re searching for the word `'earth'`, and we know that the letter `'e'` is correct in the first position
— so it’s part of the *green letters*. But if `'e'` is also listed as a *grey letter*, then a naïve filter would delete 
all words that contain `'e'`, even `'earth'` !

As with yellow letters, the solution is to count how many times each grey letter appears in a word and ensure it does 
not exceed the number of known *non-grey* occurrences. The SQL logic is very similar to the one we used for yellow letters. 
However, this time, instead of deleting words where the letter count is less than a minimum, we’ll delete words where the 
letter count is greater than a known maximum:

.. code-block:: sql

    DELETE FROM _tmp_table_name WHERE (
        (CASE WHEN letter1_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter2_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter3_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter4_id = ? THEN 1 ELSE 0 END) +
        (CASE WHEN letter5_id = ? THEN 1 ELSE 0 END) > ?
    )


This command will remove any word that contains more than the allowed occurence of a given grey letter, taking into account 
any green or yellow uses of that letter.

.. code-block:: python


    class WordleSearch():

        ...

        def search(self, target:WordleTarget, nb_words:int = -1):

            ...

            # Grey pass
            self._yellow_pass(target.grey_letters, target.green_letters, target.yellow_letters)
            if self.__len__() == 0:
                self._log("DEBUG","No word found after third pass (grey letters), returning early")
                return tuple()
            self._log("DEBUG", f"Found {self.__len__()} words after third pass (grey letters).")

            ...

        def _grey_pass(self, grey_letters:list[str], green_letters:list[str], yellow_letters:dict):

            # Check tmp table
            if not self._tmp_table_name:
                self._log("ERROR", "No temporary table, aborting")
                return

            if len(grey_letters) == 0:
                self._log("DEBUG", "No grey letters, returning early.")
                return

            # Iterate over the grey letters:
            for letter, poss in grey_letters.items():

                # Filtrate based on occurence
                l_id = self._db.get_letter_id(letter)
                max_occ = 1 + sum( [1 for gl in green_letters if letter == gl] ) + sum( [1 for yl in yellow_letters.keys() if letter == yl] ) 
                self._db.execute(
                    f"DELETE FROM {self._tmp_table_name} WHERE (" + \
                        "(CASE WHEN letter1_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter2_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter3_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter4_id = ? THEN 1 ELSE 0 END) +" + \
                        "(CASE WHEN letter5_id = ? THEN 1 ELSE 0 END) > ?" + \
                    ")",
                    (l_id, l_id, l_id, l_id, l_id, max_occ)
                )

                self._db.commit()

One shot search
---------------

While it’s great to be able to perform a search, the current process is a bit cumbersome for the user. They must first 
create a :class:`WordleDatabase`, then build a :class:`WordleTarget`, and finally create a :class:`WordleSearch`. Even 
after all that, they still need to call the search method, retrieve the result, and clean up afterward.

This is quite a hassle — especially for someone who just wants to perform a quick, one-off search. To make the experience 
more user-friendly, we can implement a helper function that takes the path to a database and a :class:`WordleTarget`, and 
then handles the entire search process from start to finish.

Fortunately, this is easy to implement:

.. code-block:: python

    def oneshot_search(db_file:str, target:WordleTarget, nb_words:int=-1) -> tuple:

        # Construct database and search:
        log = Logueur.get_loggingFunc()
        db = WordleDatabase(db_file)
        search = WordleSearch(db)

        # Conduct the search
        log("DEBUG",f"Quick search of {nb_words if nb_words > 0 else 'INF'} words for:\n{target}")
        rslt = search.search(target,nb_words)

        # Clean up and exist
        search.clean()
        return rslt

What is next
------------

With the *core/search.py* script being done, the *core* module is now finished ! The next step will be to develop
a small *CLI* application that will use this module. In the next part, we will stop using default logging function
of :mod:`py_utils.Logueur` and define a real :class:`~py_utils.Logueur.Logueur` to handle the different log messages.
