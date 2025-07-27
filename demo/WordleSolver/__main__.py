from py_utils.Logueur import ConsoleLogueurFactory

from .cli.parser import parser
from .cli.database import main_db

def main():

    # Parse arg and create logueur
    args = parser.parse_args()
    log = ConsoleLogueurFactory(level=args.log_level)
    log._messageFormat = "{body}\n"

    log.info("Hello Wordle !!\n")
    if args.cmd == "db":
        main_db(log,args.action,args.file,args.url)
    

if __name__ == "__main__":
    main()