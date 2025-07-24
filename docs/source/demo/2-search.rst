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
and a list of positions where the letter is not as the value.

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
It will display the word by replacing unknown letters with the `'*'` character, then append the dictionary
of yellow letters (prefixed with `'-c'`) and the list of grey letters (prefixed with `'-v'`):

.. code-block:: python

    class WordleTarget():

        ...

        def __repr__(self) -> str:
            word = ''.join([letter if letter else '*' for letter in self.green_letters])
            return f"'{word}' -c {self.yellow_letters} -v {self.grey_letters}"


Initialisation of the search
----------------------------

Now that we have implemented what to search, we can start implementing the search. The search will consist of deleting some 
words of a table, respecting the clues given by Wordle. To avoid having to reconstruct the entire database each time we have 
to conduct a search, we will create a temporary table. Every time we will trim the temporary table, we will first delete all 
words that don't have the knowed green letters at the correct place, then delete the words that don't contain the yellow 
letters at all and the one that posses the yellow letter but at a uncorrect place. Finally, we will delete all words that 
contain a grey letters.

The :class:`WordleSearch` will contain 3 main attributs:

- A log function like the one defined in the :class:`WordleDatabase`,
- A :class:`WordleDatabase` instance in wich to search,
- A string containing the name of a table in wich the search will be conducted.

.. code-block init

As you can see, the `_tmp_table_name` is initialized with `None` as the value. We will explain why in few moment, but for now
we will define the destructor of the :class:`WordleSearch`. Because we have maybe created a table while doing the search, we 
need to remove it at the end ! 

This is easily done:

.. code-block del

Last thing before we move to implementing the search, we will implement the same 2 dunder methods that we implemented in the 
:class:`WordleDatabase`: the :meth:`__len__` and the :meth:`__contains__` method. The logics will be the same as for the 
:class:`WordleDatabase`, but on the temporary table instead of the *words* table.

.. code-block len & contains

Conducting a search
-------------------

.. Introduction to implement the start of the search method. Remind that we do the search in three steps, remind why, and implement
.. this logic (with search in # as we don't have implemented it for now).

First pass
~~~~~~~~~~

.. need to explain how we can create the table if it's the first pass or delete
.. from the tmp table when it's not.

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

