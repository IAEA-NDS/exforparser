# https://stackoverflow.com/questions/11325135/parsing-a-structured-text-file-in-python-pyparsing
# https://stackoverflow.com/questions/24478369/parsing-relatively-structured-text-files-in-python-and-inserting-in-mongodb
# https://stackoverflow.com/questions/59159168/python-parse-semi-structured-text-and-extract-to-structed-data
from operator import index
from pyparsing import *
import itertools
import json

from .utilities import extract_key, flatten_list
from .exfor_field import *


def parse_reaction_field(subent_body) -> list:
    s = "".join(subent_body)
    """ 
    field_body returns nested list with pointer
    e.g.
    [['1', '(48-CD-0(P,X)49-IN-107,,SIG)'], ['2', '(48-CD-0(P,X)49-IN-109,,SIG)']]
    """
    try:
        reaction_field = reaction_column.search_string(s)[0].asList()
    except:
        print("parse reaction field error")
        reaction_field = ""

    return reaction_field


def get_reaction(reaction_field) -> dict:
    if reaction_field:
        previous_pointer = ""
        x4reactions_str = {}
        temp_complex_reaction = ""
        text_row = []
        freetext = {}
        ratio = False
        react = {}

        for _, val in enumerate(reaction_field):
            pointer = val[0]

            if previous_pointer == "":
                previous_pointer = val[0]  # val[0]

            if (
                val[1].startswith("((")
                or (
                    val[1].startswith("(")
                    and val[1].endswith("))")
                    and not any(i in val[1] for i in ("(PHY))", "(A))"))
                )
                or ratio
            ):
                """
                catch ratio and skip
                """
                if pointer == " ":
                    pointer = "XX"
                temp_complex_reaction += val[1]

                if val[1].endswith("))"):
                    x4reactions_str[pointer] = {
                        "x4code": temp_complex_reaction,
                        "freetext": [""],
                    }
                ratio = True
                continue

            elif val[1].startswith("(") and (
                not any(l in val[1] for l in (")=", ")/", ")+", ")-", ")*", "))"))
                or any(i in val[1] for i in ("(PHY))", "(A))"))
            ):
                if pointer == " ":
                    pointer = "XX"

                """ not ratio reaction """
                x4reactioncode = reaction_code.parse_string(val[1])

                if ratio:
                    continue

                else:
                    """separation of reaction elements"""
                    target = x4reactioncode.get("target")
                    process = x4reactioncode.get("react_process")
                    observable = x4reactioncode.get("observable")

                if observable:
                    sf49 = observable.split(",")
                    sf4 = len(sf49) > 0 and sf49[0] or None
                    sf5 = len(sf49) > 1 and sf49[1] or None
                    sf6 = len(sf49) > 2 and sf49[2] or None
                    sf7 = len(sf49) > 3 and sf49[3] or None
                    sf8 = len(sf49) > 4 and sf49[4] or None
                    sf9 = len(sf49) > 5 and sf49[5] or None

                # x4reactions_str += [[pointer, x4reactioncode[0]]]
                """
                reaction information
                """
                x4reactions_str[pointer] = {
                    "x4code": x4reactioncode[0],
                    "target": target,
                    "process": process,
                    "sf4": sf4,
                    "residual": None,
                    "sf5": sf5,
                    "sf6": sf6,
                    "sf7": sf7,
                    "sf8": sf8,
                    "sf9": sf9,
                    "freetext": [],
                }

                """
                free text after reaction code
                """
                after_text = reaction_text.search_string(val[1])

                ### search_string will return nested list: e.g. [[See Fig.5(4)]]
                if after_text[0][0]:
                    text_row += [[pointer, after_text[0][0]]]

            else:  # free text rows
                text_row += [[previous_pointer, val[1]]]

            if pointer != " ":
                previous_pointer = pointer

        """
        merge freetext var = "\n".join(myList)
        """
        freetext = {
            pointer: [t[1] for t in txt]
            for pointer, txt in itertools.groupby(text_row, extract_key)
        }

        """
        merge reaction and freetext
        """
        if x4reactions_str:
            react = dict(x4reactions_str)
            for pointer, val in freetext.items():
                react[pointer]["freetext"] += val

        # print(json.dumps(x4reactions_str, indent=1))

    else:
        react = {}

    return react


# class EnryReactions(Entry, Subentry):
#     def get_reactions(self) -> dict:
#         reactions = {}
#         ## get reaction code if the sumentnum >= 002
#         if len(self.subents_nums) > 1:
#             for s in self.subents_nums[1:]:
#                 sub = Subentry(s, self.entry_body[s])
#                 reactions[s] = sub.parse_reaction()
#         else:
#             print("no field contains REACTION")

#         # return json.dumps(reactions, indent=1)
#         return reactions


