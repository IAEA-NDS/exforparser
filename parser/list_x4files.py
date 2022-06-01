####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
# 
# Disclaimer: The code is still under developments and not ready 
#             to use. It has beeb made public to share the progress
#             between collaborators. 
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import os
import time
import hashlib

from path import EXFOR_ALL_PATH

# need version check based on the hash then the only new files should be processed


"""
Run dos2unix for all .x4 files beforehand as follows:
for f in /Users/okumuras/Documents/nucleardata/EXFOR/X4all/*/*.x4; do dos2unix "$f"; done
"""


def index_pickel_road():
    from path import INDEX_PICKEL
    from parser.exceptions import NoPickelExistenceError

    try:
        df = pd.read_pickle(INDEX_PICKEL)
        return df
    except FileNotFoundError:
        raise NoPickelExistenceError(INDEX_PICKEL)


def exfor_x4allfiles(df):
    entries = []
    for _, row in df.iterrows():
        entry = row[0]
        entries += [entry]

    return entries


## loop over all entries and compose the database
def list_exfor_files():
    from datetime import date
    from parser.exceptions import Nox4FilesExistenceError

    files = []
    entries = []

    if os.path.exists(EXFOR_ALL_PATH):
        dirs = os.listdir(EXFOR_ALL_PATH)
        for d in dirs:
            files += os.listdir(os.path.join(EXFOR_ALL_PATH, d))
    else:
        Nox4FilesExistenceError(EXFOR_ALL_PATH)

    for file in files:
        current_file = os.path.join(EXFOR_ALL_PATH, file[:3], file)
        entry = file.split(".", 1)[0]
        last_modifieddate = check_modification(current_file)
        hash = generate_hash(current_file)
        entries.append([entry, last_modifieddate, hash])

    df = pd.DataFrame(entries, columns=["entry", "last modifid", "hash"])

    """ need clean up """
    df.to_pickle(INDEX_PICKEL)

    return entries


def check_modification(f):
    return time.ctime(os.path.getmtime(f))


def rundos2unix():
    glob = os.path.join(EXFOR_ALL_PATH, "*", "*.x4")
    os.system('for f in glob; do dos2unix "$f"; done')


def generate_hash(current_file):
    from parser.exceptions import x4FileOpenError

    h = hashlib.sha1()
    try:
        with open(current_file, "rb") as file:
            chunk = 0
            while chunk != b"":
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)
    except:
        x4FileOpenError(current_file)

    return h.hexdigest()


def compare_hash(df):
    """compare all hash between old and new dataframe"""


if __name__ == "__main__":
    list_exfor_files()
    # read_exfile()
