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
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent

ENV = "dev"  # or "INT" or "PROD"


if ENV == "dev":
    DATA_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"
    OUT_PATH = "/Users/okumuras/Documents/nucleardata/EXFOR/"

elif ENV == "int":
    DATA_DIR = "/srv/data/dataexplorer_v2/"
    OUT_PATH = "/srv/data/dataexplorer_v2/out/"

elif ENV == "prod":
    DATA_DIR = "/nds/data/dataexplorer_v2/"
    OUT_PATH = "/nds/data/dataexplorer_v2/out/"


EXFOR_MASTER_REPO_PATH = os.path.join(DATA_DIR, "exfor_master")
EXFOR_DB = os.path.join(DATA_DIR, "exfortables_test.sqlite")


BUF_SIZE = 65536


""" Pickle path of list of EXFOR master files made by parser.list_x4files.py """
ENTRY_INDEX_PICKLE = os.path.join(BASE_DIR, "pickles/entry.pickle")
INSTITUTE_PICKLE = os.path.join(BASE_DIR, "pickles/institute.pickle")
ENTRY_DOI_PICKLE = os.path.join(BASE_DIR, "pickles/entry_dois.pickle")
REF_DOI_PICKLE = os.path.join(BASE_DIR, "pickles/ref_metadata.pickle")


""" Pickle path of list of EXFOR master files made by parser.list_x4files.py """
SITE_DIR = site.getsitepackages()[0]
INSTITUTE_PICKLE = os.path.join(
    SITE_DIR, "exfor_dictionary", "pickles/institute.pickle"
)


""" SQL database """
engines = {
    "exfor": create_engine("sqlite:///" + EXFOR_DB),
    # "endftables": create_engine("sqlite:///" + ENDFTAB_DB),
}

session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engines["exfor"])
)


""" Not used """
# MASS_RANGE_FILE = os.path.join(EXFOR_MASTER_REPO_PATH, "submodules/A_min_max.txt")
# MT_DEF = os.path.join( EXFOR_PARSER, "tabulated/MTall.dat" )
# MF3_JSON = os.path.join( EXFOR_PARSER, "tabulated/mf3.json" )
