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

DICTIONARY_URL = "https://nds.iaea.org/nrdc/ndsx4/trans/dicts/"
DICTIONARY_PATH = "/Users/sin/Dropbox/Development/exforparser/dictionary/"

""" EXFOR master file path """
EXFOR_ALL_PATH = "/Users/sin/Documents/nucleardata/EXFOR/X4all/"

""" Pickle path of list of EXFOR master files made by parser.list_x4files.py"""
ENTRY_INDEX_PICKLE = "pickles/entry.pickle"

""" Pickle path of list of all reactions made by indexing.py """
REACTION_INDEX_PICKLE = "pickles/reactions.pickle"

TO_JSON = True
POST_DB = False

OUT_PATH = "examples/"

MONGOBASE_URI = "https://data.mongodb-api.com/app/data-qfzzc/endpoint/data/beta/"
API_KEY = "uLxfjSQjf2YCyPxocPHHla22HTHoEA6IGpXBlToaddOqN7V3QHV0iNbVGCuFulTW"
DB_KEY = "nds:9ZCo6KYA8XYbTy1G"  ## read only account


import os
def check_x4alldir():
    from parser.exceptions import Nox4AllDirExistenceError

    if os.path.isdir(EXFOR_ALL_PATH):
        return True
    else:
        raise Nox4AllDirExistenceError(EXFOR_ALL_PATH)
