EXFOR_ALL_PATH = "/Users/okumuras/Documents/nucleardata/EXFOR/X4all/"
INDEX_PICKEL = "pickles/entry.pickle"

DICTIONARY_URL = "https://nds.iaea.org/nrdc/ndsx4/trans/dicts/"
DICTIONARY_PATH = "dictionary/"

OUT_PATH = "/Users/okumuras/Desktop/"

MONGOBASE_URI = "https://data.mongodb-api.com/app/data-qfzzc/endpoint/data/beta/"
API_KEY = "uLxfjSQjf2YCyPxocPHHla22HTHoEA6IGpXBlToaddOqN7V3QHV0iNbVGCuFulTW"
DB_KEY = "nds:9ZCo6KYA8XYbTy1G"

import os


def check_x4alldir():
    from parser.exceptions import Nox4AllDirExistenceError

    if os.path.isdir(EXFOR_ALL_PATH):
        return True
    else:
        raise Nox4AllDirExistenceError(EXFOR_ALL_PATH)
