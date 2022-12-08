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
import logging

logging.basicConfig(filename="parsing.log", level=logging.DEBUG, filemode="w")

from config import TO_JSON, POST_DB, OUT_PATH, REACTION_INDEX_PICKLE
from utilities.operation_util import del_outputs, print_time, get_entry_update_date
from parser.list_x4files import good_example_entries, list_entries_from_df
from parser.exfor_entry import Entry
from parser.exfor_subentry import Subentry
from mongodb import post_one_mongodb, post_many_mongodb
from indexing import reaction_indexing


update_date = get_entry_update_date()


def write_dict_to_json(entnum, dic):
    """
    bib info write into json file
    """
    dir = os.path.join(OUT_PATH, "json", entnum[:3])

    if len(entnum) == 5:
        if os.path.exists(dir):
            # del_outputs(dir)
            pass

        else:
            os.mkdir(dir)

    file = os.path.join(dir, entnum + ".json")

    with open(file, "wt") as json_file:
        json.dump(dic, json_file, indent=2)


# @process_time
def convert_exfor_to_json(entnum=None):
    entry_json = {}
    entry = Entry(entnum)

    sub = Subentry("001", entry.entry_body["001"])
    entry_json["entry"] = entnum
    entry_json["last_updated"] = update_date[entnum]["last_update"]
    entry_json["number_of_revisions"] = update_date[entnum]["revisions"]
    entry_json["histories"] = sub.parse_main_history_dict()
    # try:
    #     entry_json["histories"] = sub.parse_main_history_dict()
    # except:
    #     entry_json["histories"] = []

    entry_json["bib_record"] = sub.parse_main_bib_dict()

    entry_json["data_tables"] = {}
    entry_json["experimental_conditions"] = {}


    for subent in entry.subents_nums:
        sub = Subentry(subent, entry.entry_body[subent])

        entry_json["experimental_conditions"][subent] = {}
        entry_json["data_tables"][subent] = {}

        ## Check subentry body parse
        # print(entry.entry_body[subent])

        ## Check block parse
        # print(sub.get_bib_block())

        ## Check BIB
        # print( json.dumps(sub.parse_bib_identifiers(), indent=1))


        # Extra information from BIB
        entry_json["experimental_conditions"][subent] = sub.parse_extra_bib_dict()

        ## REACTION
        if subent != "001":
            entry_json["data_tables"][subent]["reaction"] = sub.parse_reaction_dict()

        ## COMMON
        entry_json["data_tables"][subent]["common"] = sub.parse_common()

        ## DATA
        if subent != "001":
            entry_json["data_tables"][subent]["data"] = sub.parse_data()

    return entry_json


def convert_json_to_exfor(entry_json):
    
    pass




def main():
    ent = list_entries_from_df()
    entries = random.sample(ent, len(ent))
    # entries = good_example_entries
    # entries = [
    #     "14545" ,"14745" , "14537", "10963", "40396", "C0380", "M0450", "O0529","C2152", "D4030", "14606", "30501", "14606","20010","30328"]

    del_outputs(OUT_PATH + "json/")

    start_time = print_time()
    logging.info(f"Start processing {start_time}")

    i = 0
    for entnum in entries:
        print(entnum)
        # entry_json = convert_exfor_to_json(entnum)
        # write_dict_to_json(entnum, entry_json)
        # post_one_mongodb("exfor_json", entry_json)
        try:
            entry_json = convert_exfor_to_json(entnum)
            write_dict_to_json(entnum, entry_json)
            post_one_mongodb("exfor_json", entry_json)
        #     # reaction_indexing(e)

        except:
            logging.error(f"ERROR: at ENTRY: {entnum}")

        i += 1

        if i > 1000000:
            break

    logging.info(f"End processing {print_time(start_time)}")


if __name__ == "__main__":
    main()

# INFO:root:Start processing 1667831350.597693
# ERROR:root:ERROR: at ENTRY: 30050
# ERROR:root:ERROR: at ENTRY: 40768
# ERROR:root:ERROR: at ENTRY: 30088
# ERROR:root:ERROR: at ENTRY: 40756
# ERROR:root:ERROR: at ENTRY: 40709
# ERROR:root:ERROR: at ENTRY: 40716
# ERROR:root:ERROR: at ENTRY: 30055
# INFO:root:End processing --- 2412.118987083435 seconds ---
