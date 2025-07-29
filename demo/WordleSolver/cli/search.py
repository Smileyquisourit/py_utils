import re

from py_utils.Logueur import Logueur

from ..core.database import _ALL_LETTERS
from ..core.search import WordleTarget, oneshot_search

def main_search(
        log:Logueur, db_filename:str, 
        green_letters:str,
        yellow_letters: str = "",
        grey_letters: str = "",
        n_word:int = 15
    ):

    log.debug(
        "Starting search action using the following args:\n" + \
        f"  - {db_filename=}\n" + \
        f"  - {green_letters=}\n" + \
        f"  - {yellow_letters=}\n" + \
        f"  - {grey_letters=}\n" + \
        f"  - {n_word=}" 
    )

    # Reconstruct target using green letters
    word = green_letters.lower()
    if len(word) != 5:
        log.error(f"There should only be 5 green letters, but I've received {len(word)} !")
    target = WordleTarget(
        first  = word[0] if word[0] in _ALL_LETTERS else None,
        second = word[1] if word[1] in _ALL_LETTERS else None,
        third  = word[2] if word[2] in _ALL_LETTERS else None,
        fourth = word[3] if word[3] in _ALL_LETTERS else None,
        fifth  = word[4] if word[4] in _ALL_LETTERS else None
    )

    # Reconstruct yellow letters
    if yellow_letters != "":
        pattern = re.compile(r'(?P<letter>[a-zA-Z])\s*\[(?P<pos>[\d,]+?)\]')
        matches = pattern.findall(" ".join(yellow_letters))
        if len(matches) == 0:
            log.warning("No yellow letters found, there is an error in the format !")
        for letter, pos in matches:
            
            # Check letter
            if not letter in _ALL_LETTERS:
                log.warning(f"Unrecognized letter {letter} in option contain ('{letter} [{pos}].\nIgnoring it.')")
                continue

            # Check position
            try:
                exclude_pos = tuple( [int(p) for p in pos.split(",")] )
            except Exception as e:
                log.warning(f"Error while trying to convert a position (letter) into a int: '{pos}':\n{e}")
                continue

            if letter in target.yellow_letters.keys():
                log.warning(f"The letter '{letter}' was specified twice, ignoring the second time {exclude_pos}.")
                continue
            log.debug(f"Adding letter '{letter}' to exclude at position {exclude_pos}")
            target.yellow_letters[letter] = exclude_pos
    else:
        log.debug("No yellow letters")

    # Reconstruct grey letters
    if grey_letters != "":
        for pos,letter in enumerate(grey_letters,start=1):
            if not letter in _ALL_LETTERS:
                log.warning(f"Unrecognized letter {letter} in option invert-match ('{letter} [{pos}]').\nIgnoring it.")
                continue

            log.debug(f"Adding letter '{letter}' to exclude set.")
            target.grey_letters.append(letter)
    else:
        log.debug("No grey letters")

    # Search
    log.info(f"Starting to search {n_word if n_word > 0 else 'all'} words correpsonding to the following target:\n{target}\n")
    words, tot_words = oneshot_search(db_filename,target,n_word)
    log.info(f"Found {tot_words} correpsonding to the target!")
    
    # Print results
    log.info(f"Words found:\n  - "+"\n  - ".join(words))
