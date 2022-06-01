####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
# 
# Disclaimer: The code is still under developments and not ready 
#             to use. It has beeb made public to share the progress
#             between collaborators. 
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import re

from .exfor_bib import *
from .exfor_reaction import *
from .exfor_data import *
from .utilities import process_time


# @process_time
def chop_subentry(subent_body, sec_name):
    """chop subent into section: BIB, COMMON, DATA"""
    body = []
    flag = False
    for line in subent_body:
        if line[0:11].strip() == "NO" + sec_name:  # if NOCOMMON etc
            body = ["NO" + sec_name]

        if line[0:11].strip() == sec_name and flag == False:
            if re.match(r"DATA\s{10,15}", line) or sec_name == "COMMON":
                flag = True
            else:
                body = [line]
                flag = True

        elif line[0:11].strip() == "END" + sec_name:
            body += [line]
            flag = False
            break

        if flag == True:
            body += [line]
    return body


"""
 Subentry class takes care of sections under the subentnum001-0XX 
"""
class Subentry:
    def __init__(self, subentnum, subent_body):
        self.subentnum = subentnum
        self.subent_body = subent_body
        """ 
        subent_body is given in dictionary format for all subentries in the entry like:
        {'001': ['SUBENT        31754001   20150330   20150817   20150706       3170\n'
                :
                'ENDSUBENT           10\n']}
        here separate them into BIB and COMMON section
        and get detailed field data
        """


    def bib_block(self) -> list:
        return chop_subentry(self.subent_body, "BIB")

    def common_block(self) -> list:
        return chop_subentry(self.subent_body, "COMMON")

    def data_block(self) -> list:
        return chop_subentry(self.subent_body, "DATA")


    def parse_bib_extra_dict(self) -> dict:
        if self.bib_block() is None:
            return "no bib"
        else:
            return bib_extra_dict(self.bib_block())


    def parse_data_heads(self) -> dict:
        if self.subentnum == "001":
            return None
        elif self.data_block()[0] == "NODATA":
            return None
        else:
            # newdata = [ [ float(d.get_unit_factor(data_block["units"][l])) * float(dp) for dp in data_block["data"][str(l)] ] for l in locs ]
            return get_heads(self.data_block())


    def parse_data(self) -> dict:
        if self.subentnum == "001":
            return None
        elif self.data_block()[0] == "NODATA":
            return None
        else:
            # newdata = [ [ float(d.get_unit_factor(data_block["units"][l])) * float(dp) for dp in data_block["data"][str(l)] ] for l in locs ]
            return recon_data(self.data_block())


    def parse_common_heads(self) -> dict:
        if self.common_block()[0] == "NOCOMMON":
            return None
        else:
            # newdata = [ [ float(d.get_unit_factor(data_block["units"][l])) * float(dp) for dp in data_block["data"][str(l)] ] for l in locs ]
            return get_heads(self.common_block())

    def parse_common(self) -> dict:
        if self.common_block()[0] == "NOCOMMON":
            return None
        else:
            return recon_data(self.common_block())


    def parse_reaction(self) -> dict:
        reaction_field = parse_reaction_field(self.subent_body)

        return get_reaction(reaction_field)





class MainSubentry(Subentry):
    def __init__(self, subentnum, subent_body):
        super().__init__("001", subent_body)
        self.subentnum = "001"
        self.main_bib_dict = self.parse_main_bib_dict()
        # self.main_mesurement_condition_dict = self.parse_bib_extra_dict()

    def parse_main_bib_dict(self) -> dict:
        if self.bib_block is None and self.subentnum != "001":
            pass
        else:
            return main_bib_dict(self.bib_block())

