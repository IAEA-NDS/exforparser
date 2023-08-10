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
import sys

sys.path.append("../")
from ..config import EXFOR_MASTER_REPO_PATH
from .exfor_subentry import Subentry
from .exfor_block import get_block


def get_entry_update_date():
    d = {}
    file = os.path.join(EXFOR_MASTER_REPO_PATH, "entry_updatedate.dat")
    with open(file) as f:
        for line in f:
            x = line.split(" ")
            d.update({x[0]: {"last_update": x[1], "revisions": x[2].strip()}})
    return d


def open_read_file(filename=""):
    """
    separate and convert all subentries into dictionary
    """
    # filename = self.generate_x4filename()
    from .exceptions import x4FileOpenError

    try:
        with open(filename, "rU") as f:
            # entry_body = f.readlines()
            return f.read().splitlines()  # as entry_body
    except:
        raise x4FileOpenError()


def diff_check():
    """
    check hash
    """
    pass


class Entry:
    def __init__(self, entnum):

        self.entnum = entnum
        self.x4filename = self.x4filename()
        self.entry_body = self.get_entry_body()
        self.subents_nums = self.get_subent_nums()

    @property
    def entry_number(self):
        if self._check_entry_nlen(self.entnum):
            return self.entnum

    def __repr__(self):
        return "Processing ... <" + self.entnum + ">"

    def __str__(self):
        return "Processing ... <" + self.entnum + ">"

    @staticmethod
    def _check_entry_nlen(entnum):
        from .exceptions import Incorrectx4Number

        if len(entnum) != 5:
            raise Incorrectx4Number(entnum)
        else:
            return True

    def x4filename(self):
        if self._check_entry_nlen(self.entnum):
            return os.path.join(EXFOR_MASTER_REPO_PATH, "exforall", self.entnum[:3], self.entnum + ".x4")

    def get_entry_exfor(self) -> dict:
        """return as EXFOR format"""
        return open_read_file(
            self.x4filename
        )  # contenain entry body as list of each line

    def get_entry_body(self) -> dict:
        from .exceptions import x4NoBody

        entry_body = {}
        subentry = []

        ## contenain entry body as list of each line
        lines = open_read_file(self.x4filename)

        if not lines:
            raise x4NoBody()

        for line in lines:
            ## maybe this is faster than yield
            if line.startswith(("ENTRY", "ENDENTRY", "NOSUBENT")):
                pass

            elif line.startswith("SUBENT"):
                subent_num = line[14:22][5:8].strip()
                subent_rows = line[23:33].strip()
                subentry = [line]

            else:
                subentry += [line]

            if line.startswith("ENDSUBENT"):
                entry_body[subent_num] = subentry
                subentry = ""

            # entry_body["date"] = {"created_date":created_date, "last_update":last_update}

        return dict(entry_body)

    def get_subent_nums(self) -> list:
        """
        get information from subent_body dict that looks like
        {'001': ['SUBENT        31754001...], '002'...}
        and reaturn the dictionary keys
        """
        return list(self.entry_body.keys())

    def get_dates(self):
        return list(self.entry_body.keys())

    def get_entry_bib_dict(self) -> dict:
        """
        SUBENT:  015
        REACTION   (56-BA-137(N,G)56-BA-138,,SIG,,AV)
        ERR-ANALYS (DATA-ERR) No information on the source of uncertainty
        STATUS     (TABLE) Table VI of 1978HARWELL,449,1978.
                    Values have been multiplied by 0.9833.
        HISTORY    (19760428R) Prelim. data from Musgrove (up to 60 keV)
                (19790606A) KO. Alteration and addition of data.
                (19810213U) KO. Reference added.
                (19821210A) DG. The values have been corrected,
                    insertion of corrigendum in reference, conversion
                    from ISO-QUANT to REACTION formalism.
        ENDBIB              10
        ---> convert into following dictionary format
        {
        "REACTION": {
        "0": [
        "(56-BA-137(N,G)56-BA-138,,SIG,,AV)"
        ]
        },
        "ERR-ANALYS": {
        "0": [
        "(DATA-ERR) No information on the source of uncertainty"
        ]
        },
        "STATUS": {
        "0": [
        "(TABLE) Table VI of 1978HARWELL,449,1978.",
        " Values have been multiplied by 0.9833."
        ]
        },
        "HISTORY": {
        "0": [
        "(19760428R) Prelim. data from Musgrove (up to 60 keV)",
        "(19790606A) KO. Alteration and addition of data.",
        "(19810213U) KO. Reference added.",
        "(19821210A) DG. The values have been corrected,",
        " insertion of corrigendum in reference, conversion",
        " from ISO-QUANT to REACTION formalism."
        ]
        }
        }
        """

        return get_block(self.entry_body["001"][1:-1], "BIB")

    def get_reactions(self) -> dict:
        reactions = {}
        ## get reaction code if the sumentnum >= 002
        ## this call is very slow for the entry with many subentries
        if len(self.subents_nums) > 1:
            for s in self.subents_nums[1:]:
                sub = Subentry(s, self.entry_body[s])
                reactions[s] = sub.parse_reaction()
        else:
            print("no field contains REACTION")

        # return json.dumps(reactions, indent=1)
        return reactions

    def delete_entry(self):
        pass

    def update_entry(self):
        """update if hash has been changed"""
        pass
