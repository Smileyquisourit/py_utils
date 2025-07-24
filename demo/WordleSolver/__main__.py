from py_utils.Logueur import ConsoleLogueurFactory
import os

from .core.database import WordleDatabase
from .core.search import WordleTarget

import argparse

def main():

    log = ConsoleLogueurFactory("DEBUG")

    target = WordleTarget(third='u')
    target.yellow_letters['a'] = [1,3]
    target.yellow_letters['b'] = [5]
    target.grey_letters = ['d','p','j']
    
    log.info(str(target))
    

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