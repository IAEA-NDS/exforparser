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
import os
import site

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DEVENV = True

if DEVENV:
    DATA_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"
    OUT_PATH = "/Users/okumuras/Desktop/"

else:
    DATA_DIR = "/srv/data/dataexplorer2/"
    OUT_PATH = "/srv/data/dataexplorer2/out/"



if os.path.exists("src/exforparser/parser"):
    EXFOR_PARSER = "src/exforparser/"

else:
    from importlib.resources import files
    EXFOR_PARSER = files("exforparser").joinpath("")


EXFOR_MASTER_REPO_PATH = os.path.join(DATA_DIR, "exfor_master")
EXFOR_DB = os.path.join(DATA_DIR, "exfor_tmp.sqlite")
# print(EXFOR_DB)


""" Pickle path of list of EXFOR master files made by parser.list_x4files.py """
ENTRY_INDEX_PICKLE = os.path.join( EXFOR_PARSER, "pickles/entry.pickle" )
MT_DEF = os.path.join( EXFOR_PARSER, "tabulated/MTall.dat" )

""" Pickle path of list of EXFOR master files made by parser.list_x4files.py """
SITE_DIR = site.getsitepackages()[0]
INSTITUTE_PICKLE = os.path.join( SITE_DIR, "exfor_dictionary", "pickles/institute.pickle" )


""" SQL database """
engine = create_engine("sqlite:///" + EXFOR_DB)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
session = Session()
