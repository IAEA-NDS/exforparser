####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import time
import hashlib

# need version check based on the hash then the only new files should be processed


"""
Run dos2unix for all .x4 files beforehand as follows:
for f in /Users/okumuras/Documents/nucleardata/EXFOR/X4all/*/*.x4; do dos2unix "$f"; done
"""


def index_pickel_road():
    from path import ENTRY_INDEX_PICKLE
    from parser.exceptions import NoPickelExistenceError

    try:
        df = pd.read_pickle(ENTRY_INDEX_PICKLE)
        return df
    except FileNotFoundError:
        raise NoPickelExistenceError(ENTRY_INDEX_PICKLE)


def exfor_x4allfiles(df):
    entries = []
    for _, row in df.iterrows():
        entry = row[0]
        entries += [entry]

    return entries


## loop over all entries and compose the database
def list_exfor_files():
    from path import EXFOR_ALL_PATH, ENTRY_INDEX_PICKLE
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
    df.to_pickle(ENTRY_INDEX_PICKLE)

    return entries


def check_modification(f):
    return time.ctime(os.path.getmtime(f))


def rundos2unix():
    from path import EXFOR_ALL_PATH

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


good_example_entries = [
    "G0509",  # facility has pointer
    "O0191",
    "12898",
    "11945",
    "22436",
    "D0047",
    "12898",  # pointer ratio normal, from Amanda
    "41640",
    "11945",
    "11404",
    "11201",
    "22356",
    "E1814",
    "D6054",
    "C0194",
    "14537",
    "21756",
    "13379",
    "30722",
    "30283",
    "C0396",
    # P,X SIG with ELEM/MASS
    "22374",  # heavy
    "14197",
    "32662",  # N,F with MASS
    "14529",
    "12591",
    "31431",
    "D4030",
    "21107",
    "13500",
    "23313",
    "10377",
    "20010",
    "21902",
    "E0306",
    "30328",
    "22331",
    "20802",  # facility and institute have pointer
    "21604",
    "12591",
    "32214",
    "12505",
    "32610",
    "21756",
    "30310",
    "12570",
    "32619",
    "14498",
    "30006",
    "30391",
    "31754",
    "12599",
    "D4170",
    "11905",
    "30310",
    "30391",
    "30310",
    "11905",
    "33118",
    "F1246",
    "13297",
    "32804",
    "13025",
    "D4170",
    "A0631",
    "13569",
    "A0466",
    "13545",
    "11404",
    "32800",
    "31833",
    "31754",
    "31679",
    "12599",
    "12589",
    "12598",
    "12576",
    "12560",
    "12531",
    "12593",
    "12554",
    "12544",
    "30441",
    "30125",
    "31816",
    "30275",
    "10536",
    "O1728",  # large DATA table with ELEM/MASS, Many DECAY-DATA
]

if __name__ == "__main__":
    list_exfor_files()
    # read_exfile()
