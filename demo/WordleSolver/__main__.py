from py_utils.Logueur import ConsoleLogueurFactory
import os

from .core.database import WordleDatabase, create_from_file

def main():

    log = ConsoleLogueurFactory("DEBUG")

    if not os.path.exists("words.db"):
        db = WordleDatabase.create("words.db")
    else:
        db = WordleDatabase('words.db')
    
    with open("../words.txt",'r') as f:
        words = list()
        for word in f:
            words.append(word)
            print(word)

            if len(words) >= 10:
                break
    words.append("123456")
    words.append("some$")
    
    db.update(words)

    print("Get letter id")
    print(f"  j = {db.get_letter_id("j")}")
    print(f"  $ = {db.get_letter_id("$")}")

    print("Check len and contain")
    print(f"  len = {len(db)}")
    print(f"  {words[1].strip()} in db = {words[1] in db}")

    print("execute")
    db.execute("SELECT word FROM words WHERE letter1_id = ?",(db.get_letter_id('j'),))
    print(db.fetch('one'))
    
    print("destructing db:")
    del db

if __name__ == "__main__":
    main()