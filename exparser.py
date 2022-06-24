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

from logging import raiseExceptions
import pandas as pd
import os
import random
import json
import pickle
import re
import itertools


from mongodb import (
    post_one_mongodb,
    post_many_mongodb,
    replace_one_mongodb,
    find_one_mongodb,
)
from path import TO_JSON, POST_DB, OUT_PATH, REACTION_INDEX_PICKLE
from dictionary.exfor_dictionary import *
from tabulated import exfortableformat

from parser.list_x4files import index_pickel_road
from parser.utilities import process_time, del_outputs, rescue, show_df_option
from parser.list_x4files import good_example_entries
from parser.exfor_entry import Entry
from parser.exfor_subentry import Subentry, MainSubentry


def list_entries():
    df = index_pickel_road()

    ent = []
    for _, row in df.iterrows():
        ent += [row["entry"]]
    return ent


def write_dict_to_json(entnum, dic):
    # print("write dict to json")
    """
    bib info write into json file
    """
    dir = os.path.join(OUT_PATH, "json", entnum[:3])
    if len(entnum) == 5:
        if os.path.exists(dir):
            pass
        else:
            os.mkdir(dir)

    file = os.path.join(dir, entnum + ".json")
    if os.path.exists(file):
        return
    else:
        with open(file, "w") as json_file:
            json.dump(dic, json_file, indent=2)

    return


# @process_time
def convert_bib(entries):
    for entnum in entries:
        ## rescue after crashing
        if rescue(entnum):
            continue

        print(entnum)
        entry = Entry(entnum)
        main = MainSubentry("001", entry.entry_body["001"])

        if TO_JSON:
            write_dict_to_json(
                entnum,
                dict(
                    **entry.get_entry_bib_dict(),
                    **{"experimental_conditions": main.parse_bib_extra_dict()}
                ),
            )

        if POST_DB:
            if find_one_mongodb("entry", {"entry_number": {"$eq": entnum}}):
                replace_one_mongodb(
                    "entry",
                    {"entry_number": {"$eq": entnum}},
                    dict(
                        **entry.get_entry_bib_dict(),
                        **{"experimental_conditions": main.parse_bib_extra_dict()}
                    ),
                )
                print(entnum, "replaced")
            else:
                post_one_mongodb(
                    "entry",
                    dict(
                        **entry.get_entry_bib_dict(),
                        **{"experimental_conditions": main.parse_bib_extra_dict()}
                    ),
                )
                print(entnum, "posted to MongoDb")

    return


# @process_time
def convert_entries(entries):
    """
    process entries
    """
    for entnum in entries:
        print(entnum)
        entry = Entry(entnum)

        """
        start looping over subentries
        """
        for s in entry.subents_nums:
            if s == "001":
                main = MainSubentry("001", entry.entry_body["001"])
                if TO_JSON:
                    write_dict_to_json(
                        entnum,
                        dict(
                            **entry.get_entry_bib_dict(),
                            **{"experimental_conditions": main.parse_bib_extra_dict()}
                        ),
                    )

                if POST_DB:
                    post_one_mongodb(
                        "entry",
                        dict(
                            **entry.get_entry_bib_dict(),
                            **{"experimental_conditions": main.parse_bib_extra_dict()}
                        ),
                    )

                ent_comm = main.parse_common()
                continue

            sub = Subentry(s, entry.entry_body[s])
            sbuent_reaction = sub.parse_reaction()

            sbuent_condition = sub.parse_bib_extra_dict()
            sbuent_data = sub.parse_data()

            sbuent_comm = sub.parse_common()

            if sbuent_comm is None:
                sbuent_comm = ent_comm

            elif sbuent_comm and ent_comm:
                sbuent_comm = {**ent_comm, **sbuent_comm}

            if sbuent_data is None:
                continue

            """
            COMMON, and DATA section filtering based on the pointer
            """
            pod = []
            ## In order to get DATA location relevant to the
            ## REACTION pointers, first get pointer the the keys.
            for p in [k for k in sbuent_reaction.keys()]:
                ## store all data locations that are refered by the pointer
                pod += [
                    loc
                    for loc in range(len(sbuent_data["heads"]))
                    if (" " + p) in sbuent_data["heads"][loc]
                    # if " ".join(p) in sbuent_data["heads"][loc]
                ]
                pattern = "\S+\s+\w"
                repatter = re.compile(pattern)
                opo = [
                    loc
                    for loc in range(len(sbuent_data["heads"]))
                    if repatter.match(sbuent_data["heads"][loc])
                    # if " ".join(p) in sbuent_data["heads"][loc]
                ]

            ## store the data locations that are not with pointer,
            ## which might be a running column
            # dif = set([*range(len(sbuent_data["heads"]))]) - set(pod)
            dif = set([*range(len(sbuent_data["heads"]))]) - set(opo) - set(pod)

            """
            Process COMMON and DATA based on REACTION pointers
            Note that the only REACTION pointer could be useful and
            should be considered to proecss since some entries have
            pointers but not define DATA columns (just use for the
            relationship between identifiers in the BIB).
            """
            ## Real process to devide DATA based on the REACTION pointers
            for pointer, reac_dic in sbuent_reaction.items():
                subent_dict = {}
                
                if reac_dic.get("sf6") is None or reac_dic.get("target") is None:
                    ## catch cases with ratio reaction coding
                    continue

                subent_dict["id"] = entnum + s + pointer
                subent_dict["reaction"] = reac_dic
                subent_dict["measurement_conditions"] = sbuent_condition
                # { i: {k: d[k]} for i, d in sbuent_condition.items() for k in d.keys() if k == pointer or k == "XX" }
                subent_dict["common_data"] = sbuent_comm

                if pointer == "XX":
                    subent_dict["data_table"] = sbuent_data

                if pointer != "XX":
                    ## search the DATA header that
                    ## contains pointer number such as "DATA    1"
                    tod = [
                        loc
                        for loc in range(len(sbuent_data["heads"]))
                        if (" " + pointer) in sbuent_data["heads"][loc]
                    ]
                    dl = list(dif) + tod

                    data_dict = {}
                    data_dict["heads"] = [sbuent_data["heads"][loc] for loc in dl]
                    data_dict["units"] = [sbuent_data["units"][loc] for loc in dl]
                    data_dict["data"] = [sbuent_data["data"][loc] for loc in dl]


                    subent_dict["data_table"] = data_dict

                if TO_JSON:
                    ## Here, direct conversion from EXFOR to JSON
                    write_dict_to_json(entnum + "-" + s + "-" + pointer, subent_dict)

                if POST_DB:
                    post_one_mongodb("data", subent_dict)

                reac_dic = {}

    return subent_dict


# @process_time
def convert_single(entnum=None, s=None, pointer=None):
    print("parser: ", entnum, s, pointer)
    ## rescue after crashing
    if rescue(entnum + s + pointer):
        return

    entry = Entry(entnum)
    ## parse and save bib data

    main = MainSubentry("001", entry.entry_body["001"])
    ent_comm = main.parse_common()

    if TO_JSON:
        write_dict_to_json(
            entnum,
            dict(
                **entry.get_entry_bib_dict(),
                **{"experimental_conditions": main.parse_bib_extra_dict()}
            ),
        )

    if POST_DB:
        if find_one_mongodb( "entry", {"entry_number": { "$eq" : entnum}} ):
            pass
        else:
            post_one_mongodb("entry",
            dict(
                **entry.get_entry_bib_dict(),
                **{"experimental_conditions": main.parse_bib_extra_dict()}
                )
            )

    sub = Subentry(s, entry.entry_body[s])
    sbuent_reaction = sub.parse_reaction()
    sbuent_condition = sub.parse_bib_extra_dict()
    sbuent_data = sub.parse_data()
    sbuent_comm = sub.parse_common()

    if sbuent_comm is None:
        sbuent_comm = ent_comm

    elif sbuent_comm and ent_comm:
        sbuent_comm = {**ent_comm, **sbuent_comm}

    if sbuent_data is None:
        return
        # print("no data")

    ## COMMON, and DATA section filtering based on the pointer
    pattern = "\S+\s+\w"
    repatter = re.compile(pattern)
    pod = [
        loc
        for loc in range(len(sbuent_data["heads"]))
        if (" " + pointer) in sbuent_data["heads"][loc]
        # if " ".join(p) in sbuent_data["heads"][loc]
    ]
    opo = [
        loc
        for loc in range(len(sbuent_data["heads"]))
        if repatter.match(sbuent_data["heads"][loc])
        # if " ".join(p) in sbuent_data["heads"][loc]
    ]
    ## store the data locations that are not with pointer,
    ## which might be a running column
    dif = set([*range(len(sbuent_data["heads"]))]) - set(opo) - set(pod)
    reac_dic = sbuent_reaction[pointer]
    subent_dict = {}
    ## limit to the reaction cross sections
    subent_dict["id"] = entnum + s + pointer
    subent_dict["reaction"] = reac_dic
    subent_dict["measurement_conditions"] = sbuent_condition
    subent_dict["common_data"] = sbuent_comm

    if pointer == "XX":
        subent_dict["data_table"] = sbuent_data

    if pointer != "XX":
        ## search the DATA header that
        ## contains pointer number such as "DATA    1"
        tod = [
            loc
            for loc in range(len(sbuent_data["heads"]))
            if (" " + pointer) in sbuent_data["heads"][loc]
        ]
        dl = list(dif) + tod

        data_dict = {}
        data_dict["heads"] = [sbuent_data["heads"][loc] for loc in dl]
        data_dict["units"] = [sbuent_data["units"][loc] for loc in dl]
        data_dict["data"] = [sbuent_data["data"][str(loc)] for loc in dl]

        subent_dict["data_table"] = data_dict

    if TO_JSON:
        ## Here, direct conversion from EXFOR to JSON and
        ## save entry-subentry-pointer file
        write_dict_to_json(entnum + "-" + s + "-" + pointer, subent_dict)

    if POST_DB:
        if find_one_mongodb("data", {"id": {"$eq": entnum + s + pointer}}):
            replace_one_mongodb(
                "data", {"id": {"$eq": entnum + s + pointer}}, subent_dict
            )
            print(entnum + s + pointer, "replaced")
        else:
            post_one_mongodb("data", subent_dict)
            print(entnum + s + pointer, "DATA posted to MongoDb")

    return


if __name__ == "__main__":
    """update dictionary"""
    ## get latest dictionary from NDS website
    # latest = download_latest_dict()

    ## save diction in separate json files
    # parse_dictionary(latest)

    """ flush converted files if neccessary """
    # del_outputs("json")

    """ read entry number index from pickel """
    # ent = list_entries()
    # entries = random.sample(ent, len(ent))
    # entries = good_example_entries

    ## convert bib data only
    # convert_bib(entries)

    ## convert all data into JSON
    # convert_entries(entries)

    """ run indexing -- takes 8 hours """
    # df = reaction_indexing()
    # print(df)

    """ convert selected entries from reaction_index """
    df_reaction = pd.read_pickle(REACTION_INDEX_PICKLE)

    # entry = "12515"
    # target = "41-Nb-93"
    target = "79-AU-197"
    process = "N,G"
    # process = "N,F"
    sf4 = "MASS"
    quantity = "SIG"
    sf8 = ["RES", "RTE", "SDT/AV", "SDT"]

    with pd.option_context("display.float_format", "{:11.3e}".format):
        df_select = df_reaction[
        #     # (df_reaction.entry == entry )
            (df_reaction.target == target.upper())
            & (df_reaction.process == process.upper())
            & (df_reaction.sf5.isnull())
            & (df_reaction.sf6 == quantity.upper())
            & (~df_reaction.sf8.isin(sf8))
            & (df_reaction.points > 0)
        #     # # & (df_reaction.sf4 == sf4.upper())
                    ]
        print(df_select.sort_values(by=["year","entry","subentry"]))


    # for _, row in df_select.iterrows():
    #     convert_single(row["entry"], row["subentry"], row["pointer"])

    # del_outputs("json")
    entries = df_select.entry.unique()
    convert_entries(entries)

