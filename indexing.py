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

import pandas as pd
import sys
import random
import pickle
import logging

logging.basicConfig(filename="indexing.log", level=logging.DEBUG, filemode="w")


from config import REACTION_INDEX_PICKLE, POST_DB, TO_JSON
from utilities.operation_util import print_time
from parser.exfor_entry import Entry
from parser.exfor_subentry import Subentry
from parser.exfor_field import columndef
from parser.exfor_data import product_expansion, get_inc_energy
from parser.list_x4files import good_example_entries, list_entries_from_df
from mongodb import post_many_mongodb

# sys.path.append("../exfor_dictionary/")
# from exfor_dictionary.exfor_dictionary import *


# @process_time
def reaction_indexing(entnum):

    reac_set = []
    entry = Entry(entnum)
    main = Subentry("001", entry.entry_body["001"])
    main_bib_dict = main.parse_main_bib_dict()

    for subent in entry.subents_nums[1:]:
        sub = Subentry(subent, entry.entry_body[subent])

        ## REACTION
        sbuent_reaction = sub.parse_reaction_dict()
        incident_energy = get_inc_energy(main, sub)

        if sbuent_reaction is None:
            continue

        for pointer, reac_dic in sbuent_reaction.items():
            # print(pointer, reac_dic)
            """
            reac_dic: list of reaction structure
                e.g. {'x4_code': '(30-ZN-64(N,G),,WID)', 0: {'type': None, 'target': '30-ZN-64', 'process': 'N,G', 'sf49': ',,WID', 'sf4': None, 'sf5': None, 'sf6': 'WID', 'sf7': None, 'sf8': None, 'sf9': None}, 'type': None}
            """

            meta_dict = {
                "id": entnum + "-" + subent + "-" + str(pointer),
                "entry": entnum,
                "subentry": subent,
                "pointer": str(pointer),
                "np": None,
                "year": main_bib_dict["references"][0][0]["publication_year"],
                "author": main_bib_dict["authors"][0]["name"],
                "min_inc_en": incident_energy["min"],
                "max_inc_en": incident_energy["max"],
                "points": incident_energy["points"],
            }

            ## remove unnecessary info from reac_dic
            del reac_dic["free_text"]
            del reac_dic[0]["code"]

            if reac_dic["type"] is None:
                if reac_dic[0]["sf4"] in ["ELEM/MASS", "MASS", "ELEM"]:
                    try:
                        partial_reac_set = product_expansion(
                            main, sub, dict(**meta_dict, **reac_dic[0])
                        )
                        reac_set += partial_reac_set

                    except:
                        reac_set += [dict(**meta_dict, **reac_dic[0])]

                else:
                    reac_set += [dict(**meta_dict, **reac_dic[0])]

            else:
                reac_dic[0] = {
                    "target": None,
                    "process": None,
                    "sf4": None,
                    "residual": None,
                    "sf5": None,
                    "sf6": None,
                    "sf7": None,
                    "sf8": None,
                    "sf9": None,
                    "type": reac_dic["type"],
                }
                reac_set += [dict(**meta_dict, **reac_dic[0])]

    # if reac_set:
    #     save_and_post(reac_set)

    print(reac_set)
    return reac_set


def save_and_post(reac_set):
    df = pd.DataFrame(columns=columndef, index=None)
    df = df.from_records(reac_set)

    df["np"] = df["np"].astype("Int64").fillna(0)

    try:
        reaction_df = pickle.load(open(REACTION_INDEX_PICKLE, "rb"))

    except:
        reaction_df = pd.DataFrame(columns=columndef)

    reaction_df = pd.concat([reaction_df, df])
    reaction_df = reaction_df.reset_index(drop=True)
    reaction_df.to_pickle(REACTION_INDEX_PICKLE)

    if POST_DB:
        post_many_mongodb("reaction", df.to_dict("records"))
        print("submitted to mongodb")

    return reaction_df


def main():

    ent = list_entries_from_df()
    entries = random.sample(ent, len(ent))
    entries = good_example_entries
    entries = [
        "14537",
        "14545",
        "10963",
        "40396",
        "C0380",
        "M0450",
        "O0529",
    ]  # , "C2152", "D4030", "14537", "14606", "30501", "14606","20010","30328"]

    start_time = print_time()
    logging.info(f"Start processing {start_time}")

    i = 0
    for e in entries:
        print(e)
        reaction_indexing(e)

        # try:
        #     reaction_indexing(e)

        # except:
        #     logging.error(f"ERROR: at ENTRY: {e}")

        i += 1

        if i > 1000000:
            break

    logging.info(f"End processing {print_time(start_time)}")


if __name__ == "__main__":
    main()
