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
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

DEVENV = True

if DEVENV:
    DATA_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"
    MODULES_DIR = "/Users/okumuras/Dropbox/Development/"


else:
    DATA_DIR = "/srv/data/dataexplorer2/"
    MODULES_DIR = "/srv/data/dataexplorer2/"



EXFOR_DB = DATA_DIR + "exfor.sqlite"


""" Pickle path of list of EXFOR master files made by parser.list_x4files.py"""
ENTRY_INDEX_PICKLE = "pickles/entry.pickle"


TO_JSON = True
POST_DB = False


OUT_PATH = DATA_DIR +  "../../../Desktop/"


""" SQL database """
engine = db.create_engine("sqlite:///" + EXFOR_DB)
session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
