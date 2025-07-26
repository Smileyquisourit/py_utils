from py_utils.Logueur import Logueur

import uuid

from .database import WordleDatabase

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

    def __repr__(self) -> str:
            word = ''.join([letter if letter else '*' for letter in self.green_letters])
            return f"'{word}' -c {self.yellow_letters} -v {self.grey_letters}"
    
class WordleSearch():

    def __init__(self, database:WordleDatabase):
        
        # Initialize instance
        self._log = Logueur.get_loggingFunc()
        self._db = database
        self._tmp_table_name = None

    def __del__(self):
        self.clean()

    def clean(self):
        if self._tmp_table_name:
            self._log("DEBUG",f"Found temporary table '{self._tmp_table_name}'. Deleting it.")

            try:
                self._db.execute(f"DROP TABLE {self._tmp_table_name}",tuple())
                self._db.commit()
                self._tmp_table_name = None
            except Exception as e:
                self._log("WARNING",f"There was an error while trying to delete the temporary table {self._tmp_table_name}:\n{e}")

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
    

    def search(self, target:WordleTarget, nb_words:int = -1):
            
        self._log("DEBUG",f"Starting search with target: '{target}'")

        # Green pass
        self._green_pass(target.green_letters)
        if self.__len__() == 0:
            self._log("DEBUG","No word found after first pass (green letters), returning early")
            return tuple()
        self._log("DEBUG", f"Found {self.__len__()} words after first pass (green letters).")

        # Yellow pass
        # TODO

        # Grey pass
        # TODO

        # Process return
        if nb_words <= 0:
            nb_words = self.__len__()
        self._db.execute(f"SELECT word FROM {self._tmp_table_name} LIMIT ?", (nb_words,))

        return tuple( word[0] for word in self._db.fetch('all') )
    
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

