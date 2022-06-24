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
from path import EXFOR_ALL_PATH
from .exfor_subentry import Subentry, MainSubentry


def open_read_file(filename=""):
    """
    separate and convert all subentries into dictionary
    """
    # filename = self.generate_x4filename()
    from parser.exceptions import x4FileOpenError

    try:
        with open(filename, "r") as f:
            # entry_body = f.readlines()
            return f.readlines()  # as entry_body
    except:
        raise x4FileOpenError()


def open_read_file_line(filename=""):
    """
    separate and convert all subentries into dictionary
    """
    # filename = self.generate_x4filename()
    from parser.exceptions import x4FileOpenError

    try:
        with open(filename, "r") as f:
            lines = []
            # entry_body = f.readlines()
            for line in f:
                lines += [line]
            return lines
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
        from parser.exceptions import Incorrectx4Number

        if len(entnum) != 5:
            raise Incorrectx4Number(entnum)
        else:
            return True

    def x4filename(self):
        if self._check_entry_nlen(self.entnum):
            return os.path.join(EXFOR_ALL_PATH, self.entnum[:3], self.entnum + ".x4")

    def get_entry_exfor(self) -> dict:
        """return as EXFOR format"""
        from parser.exceptions import x4NoBody

        return open_read_file(
            self.x4filename
        )  # contenain entry body as list of each line

    def get_entry_body(self) -> dict:
        from parser.exceptions import x4NoBody

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

        return dict(entry_body)

    def get_subent_nums(self) -> list:
        """
        get information from subent_body dict that looks like
        {'001': ['SUBENT        31754001...], '002'...}
        and reaturn the dictionary keys
        """
        return list(self.entry_body.keys())

    def get_entry_bib_dict(self) -> dict:
        main = MainSubentry("001", self.entry_body["001"])
        dict = main.main_bib_dict

        ## add number and reactions into dict
        dict["entry_number"] = self.entnum
        dict["reactions"] = self.get_reactions()
        return dict

    def get_entry_common_dict(self) -> dict:
        main = MainSubentry("001", self.entry_body["001"])
        return main.main_common_dict

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
