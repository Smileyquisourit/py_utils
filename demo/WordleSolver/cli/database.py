import os
import tempfile
import urllib.request

from py_utils.Logueur import Logueur

from ..core.database import WordleDatabase


def main_db(log:Logueur, action:str, filename:str, url:str=None):

    log.debug(
        "Starting database action using the following args:\n" + \
        f"  - {action=}\n"+ \
        f"  - {filename=}\n"+ \
        f"  - {url=}\n"
    )

    if action == "init":
        log.info(f"Creating the database using '{filename}' as the filename.")
        db = WordleDatabase.create(filename)
    else:
        db = WordleDatabase(filename)

    if url:
        log.info(f"Updating the database using the following url: {url}")

        with tempfile.NamedTemporaryFile('w+') as tmp_file:

            log.debug(f"Retrieving words in temporary file {tmp_file.name}")
            urllib.request.urlretrieve(url,tmp_file.name)

            log.debug(f"{os.path.getsize(tmp_file.name)} bytes downloaded, starting to parse it.")
            old_size = len(db)
            db.update(tmp_file)

            log.info(f"Added {len(db) - old_size} words in the database !")
            log.info(f"The database have now {len(db)} words.")

        pass

    if action == 'update' and not url:
        log.error("The url option is mandatory when updating the db ! Whithout it, no action are taken.")