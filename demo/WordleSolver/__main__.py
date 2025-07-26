from py_utils.Logueur import ConsoleLogueurFactory
import os

from .core.database import WordleDatabase
from .core.search import WordleTarget, WordleSearch

import argparse

def main():

    log = ConsoleLogueurFactory("DEBUG")

    target = WordleTarget(first='c')
    target.yellow_letters['a'] = [1,3]
    target.yellow_letters['p'] = [5]
    target.grey_letters = ['d','j']
    
    log.info(str(target))

    db = WordleDatabase('words.db')
    ## ========= TMP =========
    # db.execute("SELECT name FROM sqlite_master WHERE type='table'", tuple())
    # tmp_tables = [name[0] for name in db.fetch('all') if name[0].startswith('tmpSearch_')]
    # for table in tmp_tables:
    #     db.execute(f"DROP TABLE IF EXISTS {table}", tuple())
    # db.commit()
    ## ======= END TMP =======
    search = WordleSearch(db)
    search._green_pass(target.green_letters)

    print(f"len of search after _green_pass: {len(search)}")

    search.clean()
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    db_parser = subparser.add_parser("db")
    db_parser.add_argument('file',type=str)

    search_parser = subparser.add_parser("search")
    search_parser.add_argument('word')
    search_parser.add_argument('-m','--match',nargs='*')
    search_parser.add_argument('-v','--invert-match')

    args = parser.parse_args()
    print(f"received arg: {args.word}")
    print(f"received arg -m: {args.match}")
    print(f"received arg -v: {args.invert_match}")


    main()