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
