# Test script for testing the logueur.
# This temporarily replace a real test framework
# TODO: make a real test framework !!!!

from py_utils import Logueur

def test_level(log:Logueur.Logueur):
    log.debug("This is a DEBUG message",format="[{level}] {topic} :: {body}\n")
    log.info("This is a INFO message",format="[{level}] {topic} :: {body}\n")
    log.warning("This is a WARNING message",format="[{level}] {topic} :: {body}\n")
    log.error("This is a ERROR message",format="[{level}] {topic} :: {body}\n")
    log.fatal("This is a FATAL message",format="[{level}] {topic} :: {body}\n")

def test_topic():
    pass

def main():

    # Test level:
    print("Starting test for Logueur level:\n" + \
          "---------------------------------")
    print("\nDEBUG:")
    test_level(Logueur.ConsoleLogueurFactory("DEBUG",supportColor=True))
    print("\nINFO:")
    test_level(Logueur.ConsoleLogueurFactory("INFO",supportColor=True))
    print("\nWARNING:")
    test_level(Logueur.ConsoleLogueurFactory("WARNING",supportColor=True))
    print("\nERROR:")
    test_level(Logueur.ConsoleLogueurFactory("ERROR",supportColor=True))
    print("\nFATAL:")
    test_level(Logueur.ConsoleLogueurFactory("FATAL",supportColor=True))

if __name__ == "__main__":
    main()