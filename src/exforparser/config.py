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
from pathlib import Path
import site

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


ENV = "dev"

if ENV == "dev":
    DATA_DIR = os.path.expanduser("~/Documents/nucleardata")
elif ENV == "int":
    DATA_DIR = "/srv/data/dataexplorer2"
else:
    DATA_DIR = "/nds/data/dataexplorer_v2"

MASTER_GIT_REPO_PATH = os.path.join(DATA_DIR, "EXFOR", "exfor_master")
EXFOR_JSON_GIT_REPO_PATH = os.path.join(DATA_DIR, "EXFOR", "exfor_json")
EXFORTABLES_PY_GIT_REPO_PATH = os.path.join(DATA_DIR, "EXFOR", "exfortables_py")

# The parser still uses one output root for several legacy output trees.
OUT_PATH = os.path.join(DATA_DIR, "EXFOR")

""" SQLite DB """
EXFOR_DB = os.path.join(DATA_DIR, "EXFOR", "exfortables.sqlite")
ENDFTAB_DB = os.path.join(DATA_DIR, "endftables.sqlite")

BUF_SIZE = 65536

""" Pickle path of list of EXFOR master files made by parser.list_x4files.py """
BASE_DIR = Path(__file__).resolve().parent
ENTRY_INDEX_PICKLE = os.path.join(BASE_DIR, "pickles/entry.pickle")
ENTRY_INDEX_HEAD = os.path.join(BASE_DIR, "pickles/entry.head")
ENTRY_DOI_PICKLE = os.path.join(BASE_DIR, "pickles/entry_dois.pickle")
REF_DOI_PICKLE = os.path.join(BASE_DIR, "pickles/ref_metadata.pickle")

SITE_DIR = site.getsitepackages()[0]
INSTITUTE_PICKLE = os.path.join(
    SITE_DIR, "exfor_dictionary", "pickles/institute.pickle"
)


""" SQL database """
engines = {
    "exfor": create_engine("sqlite:///" + EXFOR_DB),
    "endftables": create_engine("sqlite:///" + ENDFTAB_DB),
}

session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engines["exfor"])
)
