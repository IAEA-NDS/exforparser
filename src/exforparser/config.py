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

ENV = os.environ.get("EXFOR_ENV", "dev")

_DEFAULTS = {
    "dev": {
        # "DATA_DIR": "/Volumes/LaCie/nucleardata/",
        # "OUT_PATH": "/Volumes/LaCie/nucleardata/",
        "DATA_DIR": "/Users/okumuras/Documents/nucleardata/EXFOR/",
        "OUT_PATH": "/Users/okumuras/Documents/nucleardata/EXFOR/",
    },
    "int": {
        "DATA_DIR": "/srv/data/dataexplorer_v2/",
        "OUT_PATH": "/srv/data/dataexplorer_v2/out/",
    },
    "prod": {
        "DATA_DIR": "/nds/data/dataexplorer_v2/",
        "OUT_PATH": "/nds/data/dataexplorer_v2/out/",
    },
}

_env_cfg = _DEFAULTS.get(ENV, _DEFAULTS["dev"])

DATA_DIR = os.environ.get("EXFOR_DATA_DIR", _env_cfg["DATA_DIR"])
OUT_PATH = os.environ.get("EXFOR_OUT_PATH", _env_cfg["OUT_PATH"])


EXFOR_MASTER_REPO_PATH = os.path.join(DATA_DIR, "exfor_master")
EXFOR_DB = os.path.join(DATA_DIR, "exfortables_claude.sqlite")


BUF_SIZE = 65536


""" Pickle path of list of EXFOR master files made by parser.list_x4files.py """
ENTRY_INDEX_PICKLE = os.path.join(BASE_DIR, "pickles/entry.pickle")
ENTRY_DOI_PICKLE = os.path.join(BASE_DIR, "pickles/entry_dois.pickle")
REF_DOI_PICKLE = os.path.join(BASE_DIR, "pickles/ref_metadata.pickle")

SITE_DIR = site.getsitepackages()[0]
INSTITUTE_PICKLE = os.path.join(
    SITE_DIR, "exfor_dictionary", "pickles/institute.pickle"
)


""" SQL database """
engines = {
    "exfor": create_engine("sqlite:///" + EXFOR_DB),
}

session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engines["exfor"])
)
