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
import pandas as pd
import time
import hashlib
import sys

# need version check based on the hash then the only new files should be processed

from .exceptions import *

sys.path.append("../")
from config import EXFOR_ALL_PATH, ENTRY_INDEX_PICKLE


"""
Run dos2unix for all .x4 files beforehand as follows:
for f in /Users/okumuras/Documents/nucleardata/EXFOR/X4all/*/*.x4; do dos2unix "$f"; done
"""


def check_x4alldir():
    from parser.exceptions import Nox4AllDirExistenceError

    if os.path.isdir(EXFOR_ALL_PATH):
        return True
    else:
        raise Nox4AllDirExistenceError(EXFOR_ALL_PATH)


def index_pickel_road():

    try:
        df = pd.read_pickle(ENTRY_INDEX_PICKLE)
        return df

    except FileNotFoundError:
        raise NoPickelExistenceError("../" + ENTRY_INDEX_PICKLE)


def exfor_x4allfiles(df):
    entries = []
    for _, row in df.iterrows():
        entry = row[0]
        entries += [entry]

    return entries


def list_entries_from_df():
    df = index_pickel_road()

    ent = []

    for _, row in df.iterrows():
        ent += [row["entry"]]

    return ent


def list_exfor_files():
    ## loop over all entries and compose the list of entries
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
    df.to_pickle("../" + ENTRY_INDEX_PICKLE)

    print(df)
    return entries


def check_modification(f):
    return time.ctime(os.path.getmtime(f))


def rundos2unix():
    glob = os.path.join(EXFOR_ALL_PATH, "*", "*.x4")
    os.system('for f in glob; do dos2unix "$f"; done')


def generate_hash(current_file):
    ## from parser.exceptions import x4FileOpenError

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
    "14545",
    "40396",
    "C0380",
    "M0450",
    "O0529",
    "10963",  # asymmetirc reaction (((30-ZN-64(N,EL),,WID,,G)*((30-ZN-64(N,G),,WID)+(30-ZN-64(N,EL),,WID,,FCT)))/(30-ZN-64(N,TOT),,WID))
    "14605",  # Istitute two rows with free text
    # "G0509",  # facility has pointer
    "O0191",
    "12898",
    "11945",
    "22436",
    "D0047",  # ((92-U-CMP(A,N),,PY,,TT)=(6-C-CMP(A,N),,PY,,TT))
    "12898",  # pointer ratio normal, from Amanda, ((23-V-51(N,P)22-TI-51,,SIG)/(92-U-238(N,F),,SIG))
    "41640",
    "11945",
    "11404",
    "11201",
    "22356",
    "E1814",
    "D6054",
    "C0194",
    "14537",  # R-value  (((94-PU-239(N,F)ELEM/MASS,CUM,FY,,FST)/(94-PU-239(N,F)42-MO-99,CUM,FY,,FST))//((92-U-235(N,F)ELEM/MASS,CUM,FY,,MXW)/(92-U-235(N,F)42-MO-99,CUM,FY,,MXW)))
    "21756",
    "13379",
    "30722",
    "30283",  # pointer + flag in 003 3(1.)
    "C0396",  # P,X SIG with ELEM/MASS
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
    "20010",  # REFERENCE  ((R,KFK-1000,1968)=(R,EUR-3963E,1968)= + \n (R,EANDC(E)-111,1968))
    "21902",
    "E0306",
    "30328",
    "22331",
    "20802",  # facility and institute have pointer
    "21604",
    "12591",
    "32214",  # 003 contain only SUPPL-INFO, no REACTION
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
    "31816",  # ratio ((xxx)//(ccc))
    "30275",
    "10536",
    "O1728",  # large DATA table with ELEM/MASS, Many DECAY-DATA
]

if __name__ == "__main__":
    list_exfor_files()
    # read_exfile()


# 11404 includes "  -9" in the data
# A0466 reaction flag
# 32804 wrapped DATA block
# 13545 wrapped DATA block with empty row
# 30441 no data
# D0047 O0191 freetext after reaction code
# 11905 FLAG
# 33133 MONITOR, DECAY-MON pointer
# 33118 MOTHED, DETECTOR pointer, REACTION (())/(()), FLAG
# 13569 NODATA
# A0631 (31-GA-69(A,X)32-GE-69,(CUM),SIG)
# F1246 reaction string contains *: (92-U-238(28-NI-64,FUS)120-*-302,,SIG,,MSC)
# 22436 contain many things, good for test
# https://towardsdatascience.com/how-to-use-python-classes-effectively-10b42db8d7bd
# 13297 nothing
# 32214 nodata with SUPPL-INF, Authors name contains quote
# 20802 flaged institute but data is not given with flag (ave of two individual measurement) and this is the only one case.
# 30328 flag + reaction pointer
# 30391 FLAG      4(1.) Momentum L is equal or larger than 1.
# 21604 DECAY-DATA ((1.)41-NB-96,23.4HR,DG)
# 30006002 ERR-ANALYS (ERR-T)
# 30501 MONIT-REF  ((MONIT2)31248007,S.K.Mangal+,J,NP,36,542,1962)
#                   (,Zhao Wenrong,R,INDC(CPR)-16,198908)
#                   (,,3,IRDF-2002,,2005)
# O0191007 原因不明エラー
# 21756002 MONITOR    ((79-AU-197(N,2N)79-AU-196,,SIG)//
#                     (79-AU-197(N,2N)79-AU-196,,SIG))
# 14498 MONITOR    ((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))
# 14599 MONITOR    (92-U-235(N,F)56-BA-140,(CUM),FY,,SPA)
# 14537 MONITOR    ((MONIT1)(94-PU-239(N,F)42-MO-99,CUM,FY,,FST)/
#                  (92-U-235(N,F)42-MO-99,CUM,FY,,MXW))
#                  ((MONIT2)92-U-235(N,F)ELEM/MASS,CUM,FY,,MXW)
# 32662 REACTION  1(92-U-238(N,F),,AP,LF,FIS) Mean mass of light fragmentent
#       DECAY-DATA ((1.)36-KR-85-M,4.48HR,DG,151.18,0.76)
#                  ((2.)36-KR-87,76.3MIN,DG,402.6,0.492)
#                  ((3.)36-KR-88,2.84HR,DG,196.32,0.263)
#                  ((4.)37-RB-89,15.6MIN,DG,1031.9,0.58)
# 32610 EN-SEC     (E,G)
# E0306 LEVEL-PROP ((0.)12-MG-27,E-LVL=0.000,SPIN=0.5,PARITY=+1.)
#                  ((1.)12-MG-27,E-LVL=0.987,SPIN=1.5,PARITY=+1.)
# 12591  two facilities
#       FACILITY   (REAC,1CANCRC) NRX reactor
#                  (REAC,1USAMTR) Materials Testing Reactor at Arco,
#                  Idaho
# 31698             DATA contains number apart from pointer
#                   EN-MIN     DATA       DATA-ERR   MONIT2     EN-NRM3    MONIT3
#                   EV         B          B          B          EV         B
#                   0.55       1549.      174.       13.90      0.0253     98.66
#                   ENDDATA              3
# D4030 DECAY-MON  (30-ZN-62,9.26HR,DG,548.4,0.152,
#                         DG,596.7,0.257)
#                  (30-ZN-63,38.1MIN,DG,669.8,0.084,
#                         DG,962.2,0.066)
#                  (30-ZN-65,244.1D,DG,1115.5,0.5075)
#       DECAY-DATA (39-Y-84-G,40.0MIN,DG,660.6,0.146,
#                             DG,793.0,0.98,
#                             DG,974.35,0.74).Not given by the author,
#                  taken from e. Browne, r.B.Firestone, table of
#                  radioactive isotopes, (ed. Sirley) Willey, london,
#                  1986.
# C2200 DECAY-DATA (65-TB-151-G,17.609HR,DG,616.56,0.104,
#                               DG,251.86,0.263,
#                               DG,287.36,0.283,
#                               DG,931.23,0.077)
#     "30969"       react[pointer]["freetext"] += val  KeyError: 'XX'
# D6054  (6-C-12(10-NE-20,X)ELEM,,DA/DE)
# 21429   REFERENCE  (B,PR.NUC.EN.,2,183,58)
# 30722   REACTION   ((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG)) Sigma ratio
# D6054002         No DATA given in 002-010, No incident energy for REACTION   (6-C-12(10-NE-20,X)ELEM,,DA/DE)
# 32609  REFERENCE  ((J,CNDP,8,7,1992)=(P,INDC(CPR)-029,7,1992))
#    (C,97TRIEST,1,514,1997)
#     Yu.M.Gledenov+, same cross section given
#    ((S,ISINN-3,92,1995)=(R,JINR-E3-95-307,92,1995))
#     Yu.M.Gledenov+, same cross section given
#    (J,NTC,17,129,199403)
#     Tang Guoyou+, same cross section given
#    (R,JINR-E3-93-428,1993)
#     Yu.M.Gledenov+, same cross section given
#    (C,93FRIBOU,,587,1993)
#     Yu.M.Gledenov+, same cross section given
#    (J,CNP,15,(3),239,199308)
#     Tang Guoyou+, same cross section given
