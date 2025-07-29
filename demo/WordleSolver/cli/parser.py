import argparse

from py_utils.Logueur.log_level import LogLevel

parser = argparse.ArgumentParser(
    prog = 'WordleSolver',
    description = "A simple cli application to solve the NY Times Wordle game."
)
subparsers = parser.add_subparsers(
    title = "actions",
    dest='cmd',
    required = True
)

parser.add_argument(
    "-ll", "--log-level", 
    help="The severity level of the log messages. Default to 'INFO'",
    type=LogLevel.factory,
    default=LogLevel.INFO
)

# Database Parser
# ===============

db_parser = subparsers.add_parser("db", help="Database related operations.")

db_parser.add_argument(
    "action", choices=["init","update"],
    help="The action to perfom. 'init' will create the database, and 'update' will fill it with words."
)
db_parser.add_argument(
    "file",
    help="The file name of the database."
)
db_parser.add_argument(
    "-u","--url",
    help="The url into wich the words are defined. If used with the 'init' command, it will be used to automagically " + \
    "update the database. This argument is mendatory when updating the database."
)


# Search Parser
# =============

search_parser = subparsers.add_parser("search", help="Search related operations.")

search_parser.add_argument(
    "database",
    help="The database in wich to search."
)
search_parser.add_argument(
    "green_letters",
    help="The word to search. Replace the letters you don't know by '*'"
)
search_parser.add_argument(
    "-c", "--contain",
    help="Letter that is in the word, but you only know the position where it isn't. " + \
        "Give in the following format: 'l [1,2] m [2,3,5]', where l and m are the letter and the number in parentheses are the position to exclude.",
    default="", nargs="*", dest="yellow_letters"
)
search_parser.add_argument(
    "-v","--invert-match",
    help="Letters to exclude.",
    default="", dest="grey_letters"
)
search_parser.add_argument(
    "-n", "--nb-word",
    help="The number of word to return.",
    default=15, type=int, dest="n_word" 
)

