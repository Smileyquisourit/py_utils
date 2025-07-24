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