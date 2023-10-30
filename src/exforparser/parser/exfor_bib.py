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

from pyparsing import *

from .exfor_field import *
from .exfor_block import get_identifier_details


def correct_pub_year(ref):

    year = ref.replace("(", "").replace(")", "").split(",")[-1]

    if len(year) == 2:
        return "19" + year

    elif len(year) == 4:
        if year.startswith("20") or year.startswith("19"):
            ## 1960 or 2020
            return year

        elif not year.startswith("19"):
            ### 8811
            return "19" + year[0:2]

    elif len(year) == 6:
        if year.startswith("20"):
            ### 200109
            return year[0:4]

        elif year.startswith("19"):
            ###  196809
            return year[0:4]

        elif not year.startswith("19") and not year.startswith("20"):
            ###  680901, most of the case it could be 19s
            return "19" + year[0:2]

    elif len(year) == 8: 
        ### 20001120
        return year[0:4]

    else:
        return year


def parse_history_bib(bib_block) -> dict:
    return get_identifier_details(bib_block["HISTORY"]["0"])


def parse_main_bib(bib_block) -> dict:
    """
    return the bibliographic information (TITLE, AUTHORS, INSTITUTE, REFERENCE only) 
    Input:
        bib_block: { pointer: [list of rows] }
                   e.g. {0: ['(VDG,3CPRBJG) 4.5 MV Van de Graaff']}
    Output:
    bib_dict = {
                "title": "",
                "authors": [{"name": "A.B. Smith"}],
                "institutes": [{"x4_code": "(xxxxx)"}],
                "references": {pointer: [ {"x4_code": (xxxxx)}, {"x4_code": (xxxxx)} ]},
                "facilities": {pointer: [ {"x4_code": (xxxxx), "facility_type": () } ]},
                }
    """

    bib_dict = {
        "title": "",
        "authors": [],
        "institutes": [],
        "references":  [],
        "facilities": [],
    }

    for identifier in main_identifiers:
        """
        identifier: TITLE, AUTHOR, INSTITUTE, FACILITY, REFERENCE
        indentifier_body: list of lines
            e.g. in C1823
            ['(Jenny Lee,M.B.Tsang,D.Bazin,D.Coupland,V.Henzl,', 'D.Henzlova,M.Kilburn,W.G.Lynch,A.M.Rogers,', 'A.Sanetullaev,Z.Y.Sun,M.Youngs,R.J.Charity,', "L.G.Sobotka,M.Famiano,S.Hudan,D.Shapira,P.O'Malley,", 'W.A.Peters,K.Y.Chae,K.Schmitt)'] ['Jenny Lee', 'M.B.Tsang', 'D.Bazin', 'D.Coupland', 'V.Henzl', 'D.Henzlova', 'M.Kilburn', 'W.G.Lynch', 'A.M.Rogers', 'A.Sanetullaev', 'Z.Y.Sun', 'M.Youngs', 'R.J.Charity', 'L.G.Sobotka', 'M.Famiano', 'S.Hudan', 'D.Shapira', "P.O'Malley", 'W.A.Peters', 'K.Y.Chae', 'K.Schmitt']
        """

        if not bib_block.get(identifier):
            ## skip if no one of the main_identifiers in the SUBENTRY-001
            continue

        for pointer, indentifier_body in bib_block.get(identifier).items():

            if identifier == "TITLE":
                title = " ".join(indentifier_body).replace("  ", " ")
                bib_dict["title"] = title
            #


            elif identifier == "AUTHOR":
                """
                A few entries has freetext afterwards a list of authors such as D0177, 40016, 30936
                """
                identifier_set = get_identifier_details(indentifier_body)
                authors = "".join(identifier_set[0]["x4_code"][1:-1]).split(",")

                bib_dict["authors"] = [
                    {"name": authors[i].title().strip()} for i in range(len(authors))
                ]


            elif identifier == "INSTITUTE":
                identifier_set = get_identifier_details(indentifier_body)

                for i in range(len(identifier_set)):

                    if identifier_set[i]["x4_code"]:
                        institutes = "".join(identifier_set[i]["x4_code"])[1:-1].split(
                            ","
                        )

                        if len(institutes) > 1:
                            free_txt = "".join(identifier_set[i]["free_txt"])
                            identifier_set.pop(i)

                            identifier_set += [
                                {
                                    "x4_code": "(" + institutes[i] + ")",
                                    "free_txt": free_txt,
                                }
                                for i in range(len(institutes))
                            ]

                bib_dict["institutes"] = identifier_set


            elif identifier == "REFERENCE":
                identifier_set = get_identifier_details(indentifier_body)

                for i in range(len(identifier_set)):
                    identifier_set[i]["publication_year"] = correct_pub_year(
                        identifier_set[i]["x4_code"]
                    )
                    identifier_set[i]["doi"] = None
                    identifier_set[i]["pointer"] = pointer

                    if identifier_set[i]["free_txt"]:
                        
                        for l in range(len(identifier_set[i]["free_txt"])):

                            if identifier_set[i]["free_txt"][l].startswith("#doi"):

                                ## extract doi and add to dictionary
                                identifier_set[i]["doi"] = identifier_set[i][
                                    "free_txt"
                                ][l].replace("#doi:", "")
                        

                                ## remove doi from free text list
                                # identifier_set[i]["free_txt"].pop(l)

                bib_dict["references"] = identifier_set


            elif identifier == "FACILITY":
                identifier_set = get_identifier_details(indentifier_body)

                for i in range(len(identifier_set)):

                    identifier_set[i]["pointer"] = pointer
                    if identifier_set[i]["x4_code"]:
                        facilities = "".join(identifier_set[i]["x4_code"])[1:-1].split(
                            ","
                        )

                        if len(facilities) > 1:
                            identifier_set[i]["facility_type"] = (
                                "(" + facilities[0] + ")"
                            )
                            identifier_set[i]["institute"] = "(" + facilities[1] + ")"

                        else:
                            identifier_set[i]["facility_type"] = identifier_set[i][
                                "x4_code"
                            ]
                            identifier_set[i]["institute"] = None
                    else:
                        identifier_set[i]["facility_type"] = None
                        identifier_set[i]["institute"] = None

                bib_dict["facilities"] = identifier_set

            # elif identifier == "HISTORY":
            #     identifier_set = get_identifier_details(indentifier_body)
            #     bib_dict["history"] = identifier_set

    return bib_dict


def parse_extra_bib(bib_block) -> dict:
    bib_dict = {}

    ## looping over identifier
    for identifier in identifiers:

        if not bib_block.get(identifier):
            continue

        for pointer, indentifier_body in bib_block.get(identifier).items():
            identifier_set = get_identifier_details(indentifier_body)
            # bib_dict[identifier.lower()] = {pointer: identifier_set}

            if bib_dict.get(str(pointer)):
                bib_dict[str(pointer)].update({identifier.lower(): identifier_set})

            else:
                bib_dict[str(pointer)] = {identifier.lower(): identifier_set}

    return bib_dict
