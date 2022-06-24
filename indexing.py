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
import os
import random
import pickle


from path import REACTION_INDEX_PICKLE, POST_DB, TO_JSON
from parser.utilities import process_time, rescue
from parser.exfor_entry import Entry
from parser.exfor_subentry import Subentry, MainSubentry
from parser.exfor_data import product_expansion, get_inc_energy
from dictionary.exfor_dictionary import *
from parser.list_x4files import index_pickel_road, good_example_entries
from mongodb import post_many_mongodb


def list_entries():
    df = index_pickel_road()

    ent = []
    for _, row in df.iterrows():
        ent += [row["entry"]]
    return ent


run_for = ["SIG"]
columndef = [
    "id",
    "entry",
    "subentry",
    "pointer",
    "np",
    "year",
    "author",
    "min_inc_en",
    "max_inc_en",
    "points",
    "target",
    "process",
    "sf4",
    "residual",
    "sf5",
    "sf6",
    "sf7",
    "sf8",
    "sf9",
]


@process_time
def reaction_indexing(entries):
    ## Current EXFOR statistics
    ## Number of ENTRY 	     24682 	experimental works
    ## Number of SUBENT     164913  data tables (can contain data of more than one reaction)
    ## Number of Datasets 	182615 	data tables of reactions
    reac_set = []

    df = pd.DataFrame(columns=columndef, index=None)

    for entnum in entries:
        print(entnum)

        ## rescue after crashing
        if rescue(entnum):
            continue

        if entnum.startswith("V"):
            continue

        entry = Entry(entnum)
        main_bib_dict = entry.get_entry_bib_dict()

        for s in entry.subents_nums:
            if s == "001":
                main = MainSubentry("001", entry.entry_body["001"])
                continue

            sub = Subentry(s, entry.entry_body[s])
            sbuent_reaction = sub.parse_reaction()
            incident_energy = get_inc_energy(main, sub)

            for pointer, reac_dic in sbuent_reaction.items():
                print(s, pointer)

                if reac_dic.get("target") is None or "((" in reac_dic["x4code"]:
                    ## skip indexing the ratio or R-value reactions
                    continue

                elif not "((" in reac_dic["x4code"]:
                    ## limit the reaction for the quantities in the list: [run_for]
                    # if not reac_dic["sf6"] in run_for:
                    #     continue
                    pass

                meta_dict = {
                    "id": entnum + s + pointer,
                    "entry": entnum,
                    "subentry": s,
                    "pointer": pointer,
                    "np": None,
                    "year": None,
                    "author": main_bib_dict["authors"][0]["name"],
                    "min_inc_en": incident_energy["min"],
                    "max_inc_en": incident_energy["max"],
                    "points": incident_energy["points"],
                }
                try:
                    meta_dict["year"] = main_bib_dict["references"][0][
                        "publication year"
                    ]
                except:
                    meta_dict["year"] = None

                ## remove unnecessary info from reac_dic
                del reac_dic["freetext"]
                del reac_dic["x4code"]

                if reac_dic["sf4"] in ["ELEM/MASS", "MASS", "ELEM"]:
                    try:
                        partial_reac_set = product_expansion(
                            main, sub, dict(**meta_dict, **reac_dic)
                        )
                        reac_set += partial_reac_set
                    except:
                        reac_set += [dict(**meta_dict, **reac_dic)]

                else:
                    reac_dic["residual"] = reac_dic["sf4"]
                    reac_set += [dict(**meta_dict, **reac_dic)]

            if len(reac_set) > 20:
                df = save_and_post(reac_set)
                reac_set = []

        if reac_set:
            df = save_and_post(reac_set)
            reac_set = []

    return df


def save_and_post(reac_set):
    df = pd.DataFrame(columns=columndef, index=None)
    df = df.from_records(reac_set)
    df = df[columndef]
    df["np"] = df["np"].astype("Int64").fillna(0)

    try:
        df_all = pickle.load(open(REACTION_INDEX_PICKLE, "rb"))
    except:
        df_all = pd.DataFrame(columns=columndef)

    df_all = pd.concat([df_all, df])
    df_all.to_pickle(REACTION_INDEX_PICKLE)
    print("saved to pickle")

    if POST_DB:
        post_many_mongodb("reaction", df.to_dict("records"))
        print("submitted to mongodb")

    return df_all


def post_index_to_mongodb():
    ## indexed pickle to MongoDB
    df = pd.read_pickle(REACTION_INDEX_PICKLE)

    # print("adding number of points column to DataFrame")
    # for _, row in df.groupby(['entry','subentry','pointer']):
    #     npcount = int(row["npcount"].values[0])
    #     row['pn'] = [ (np if npcount >1 else None ) for np in range(npcount) ]
    #     df2 = pd.concat([df2, row])

    max = len(df.index)
    print(max)
    for i in range(int(max / 100)):
        # post every 100 records
        print(i * 100, i * 100 + 100)
        post_many_mongodb(
            "reaction_index", df.iloc[i * 100 : i * 100 + 100].to_dict("records")
        )
        print("posted\n", df.iloc[i * 100 : i * 100 + 100])


if __name__ == "__main__":
    # ent = list_entries()
    # entries = random.sample(ent, len(ent))
    entries = ["40019"]

    for entnum in entries:
        try:
            reaction_indexing([entnum])
        except:
            with open(r"error.dat", "a") as fp:
                fp.write(entnum + "\n")
            pass

    if POST_DB:
        post_index_to_mongodb()
