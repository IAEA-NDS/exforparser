from logging import raiseExceptions
import pandas as pd
import os
import random
import json
import pickle
import re

from parser.utilities import process_time, del_outputs
from parser.exfor_entry import Entry
from parser.exfor_subentry import Subentry, MainSubentry
from dictionary.exfor_dictionary import *

from parser.list_x4files import index_pickel_road
from mongodb import TO_JSON, POST_DB, post_one_mongodb, post_many_mongodb
from path import OUT_PATH

run_for = ["SIG"]

good_example_entries = [
        "11945",
        "11404",
        "11201",
        "22356",
        "E1814",
        "22436",
        "D6054",
        "C0194",
        "14537",
        "21756",
        "13379",
        "30722",
        "30283",
        "C0396",
        # P,X SIG with ELEM/MASS
        "22374",  # heavy
        "14197",
        "32662",  # N,F with MASS
        "14529",
        "12591",
        "22436",
        "31431",
        "D4030",
        "21107",
        "13500",
        "23313",
        "10377",
        "20010",
        "21902",
        "E0306",
        "30328",
        "22331",
        "20802",
        "21604",
        "12591",
        "32214",
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
        "D0047",
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
        "31816",
        "30275",
        "10536",
        "O1728",  # large DATA table with ELEM/MASS, Many DECA-DATA
    ]


def list_entries():
    df = index_pickel_road()

    ent = []
    for _, row in df.iterrows():
        ent += [row["entry"]]
    return ent


def write_dict_to_json(entnum, dic):
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

    with open(file, "w") as json_file:
        json.dump(dic, json_file, indent=2)

    return


@process_time
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
            print(s)
            if s == "001":
                main = MainSubentry("001",entry.entry_body["001"])
                if TO_JSON:
                    write_dict_to_json(
                        entnum,
                        dict(
                            **entry.get_entry_bib_dict(),
                            **{"experimental_conditions": main.parse_bib_extra_dict()}
                        ),
                    )

                if POST_DB:
                    post_one_mongodb("entry", entry.get_entry_bib_dict())

                ent_comm = main.parse_common()
                continue

            else:
                pass

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
            --> this is get_y
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
                ## limit to the reaction cross sections
                if reac_dic.get("sf4") is None or reac_dic.get("target") is None:
                    continue

                elif "((" in reac_dic["x4code"]:
                    pass

                elif not "((" in reac_dic["x4code"]:
                    if not reac_dic["sf6"] in run_for:
                        # see current target in run_for list
                        continue

                    ## then create DataFrame to store reactions

                else:
                    pass

                subent_dict["id"] = entnum + "-" + s + "-" + pointer
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
                    data_dict["data"] = [sbuent_data["data"][str(loc)] for loc in dl]

                    subent_dict["data_table"] = data_dict

                if TO_JSON:
                    ## Here, direct conversion from EXFOR to JSON and
                    ## save entry-subentry-pointer file
                    write_dict_to_json(entnum + "-" + s + "-" + pointer, subent_dict)
                    ## output data in EXFORTABLES like tabulated format in the tree structure
                    # write_exfortables(
                    #     entry.get_entry_bib_dict(),
                    #     s,
                    #     pointer,
                    #     reac_dic,
                    #     subent_dict["data_table"],
                    # )
                if POST_DB:
                    post_one_mongodb("data", subent_dict)

                reac_dic = {}

    return subent_dict


# @process_time
def convert_single(entnum=None, s=None, pointer=None):

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
        post_one_mongodb("entry", entry.get_entry_bib_dict())


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

    """
    COMMON, and DATA section filtering based on the pointer
    --> this is get_y
    """
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

    subent_dict["id"] = entnum + "-" + s + "-" + pointer
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
        data_dict["data"] = [sbuent_data["data"][str(loc)] for loc in dl]

        subent_dict["data_table"] = data_dict

    if TO_JSON:
        ## Here, direct conversion from EXFOR to JSON and
        ## save entry-subentry-pointer file
        write_dict_to_json(entnum + "-" + s + "-" + pointer, subent_dict)
        ## output data in EXFORTABLES like tabulated format in the tree structure
        # write_exfortables(
        #     entry.get_entry_bib_dict(), s, pointer, reac_dic, subent_dict["data_table"]
        # )
    if POST_DB:
        post_one_mongodb("data", subent_dict)

    # return 



if __name__ == "__main__":
    """update dictionary"""
    ## get latest dictionary from NDS website
    # latest = download_latest_dict()

    ## save diction in separate json files
    # parse_dictionary(latest)

    """ delete converted files if neccessary """
    # del_outputs("json")

    """ read entry number index from pickel """
    ent = list_entries()
    entries = random.sample(ent, len(ent))
    entries = good_example_entries
    # entries = ["11404"]
    convert_entries(entries)
    
    ''' run indexing -- takes long time '''
    # df = reaction_indexing()
    # print(df)


    ''' convert selected entries '''
    # del_json()
    # try:
    #     df_all = pickle.load(open("pickle/reaction_sig.pickle", "rb"))
    # except:
    #     raiseExceptions

    # target = "47-AG-107"
    # process = "N,G"
    # with pd.option_context("display.float_format", "{:11.3e}".format):
    #     print(
    #         df_all[
    #             (df_all.target == target.upper()) & (df_all.process == process.upper())
    #         ]
    #     )

    # for i, row in df_all[df_all["product"] == "ELEM/MASS"].iterrows():
    #     convert_entry(row["entry"], row["subentry"], row["pointer"])
    #     print(row["entry"], row["subentry"], row["pointer"], "  --> processed")
    
    # convert_single("22641", "002", "XX")

