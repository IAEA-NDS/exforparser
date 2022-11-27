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


from .exfor_bib import parse_main_bib, parse_extra_bib, parse_history_bib
from .exfor_reaction import parse_primitive_reaction, parse_reaction
from .exfor_data import get_heads, recon_data
from .exfor_block import get_block, parse_block_by_pointer_identifier


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

    def get_bib_block(self) -> list:
        return get_block(self.subent_body, "BIB")

    def get_common_block(self) -> list:
        return get_block(self.subent_body, "COMMON")

    def get_data_block(self) -> list:
        return get_block(self.subent_body, "DATA")

    def parse_bib_identifiers_dict(self) -> dict:
        """
        Return format
        {
            "DECAY-MON": {
            "0": [
                "(41-NB-92-M,10.15D,DG,934.4,0.9915)\n",
                "10.15+-0.02 d, (99.15+-0.04)%\n"
                ]
            },
            "STATUS": {
            "0": [
                "(TABLE) Table on page 32 in R,INDC(CCP)-0460,2016\n",
                "                 This Subent supersedes 41240.004 data.\n"
                ]
            }
        }
        """
        return parse_block_by_pointer_identifier(self.get_bib_block()[1:])

    def parse_main_bib_dict(self) -> dict:
        if self.get_bib_block() is None and self.subentnum != "001":
            return None
        else:
            return parse_main_bib(self.parse_bib_identifiers_dict())

    def parse_main_history_dict(self) -> dict:
        if self.get_bib_block() is None and self.subentnum != "001":
            return None
        else:
            return parse_history_bib(self.parse_bib_identifiers_dict())

    def parse_extra_bib_dict(self) -> dict:
        if self.get_bib_block() is None:
            return None
        else:
            return parse_extra_bib(self.parse_bib_identifiers_dict())

    def parse_primitive_reaction_flat(self):
        reaction_field = self.parse_bib_identifiers_dict().get("REACTION")
        if reaction_field:
            return parse_primitive_reaction()

    def parse_reaction_dict(self) -> dict:
        """
        Return format  {pointer: {children{x4_code:"", 0: {"code":code, "target": target}}
        """
        reaction_field = self.parse_bib_identifiers_dict().get("REACTION")

        if reaction_field:
            return parse_reaction(reaction_field)

        else:
            return None

    def parse_data_heads(self) -> dict:
        if self.subentnum == "001":
            return None
        elif self.get_data_block()[0] == "NODATA":
            return None
        else:
            return get_heads(self.get_data_block())

    def parse_data(self) -> dict:
        if self.get_data_block()[0] == "NODATA":
            return None

        else:
            return recon_data(self.get_data_block())

    def parse_common_heads(self) -> dict:
        if self.get_common_block()[0] == "NOCOMMON":
            return None
        else:
            return get_heads(self.get_common_block())

    def parse_common(self) -> dict:
        if self.get_common_block()[0] == "NOCOMMON":
            return None
        else:
            return recon_data(self.get_common_block())
