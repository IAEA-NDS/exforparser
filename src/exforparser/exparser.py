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
import json
import logging

logging.basicConfig(filename="parsing.log", level=logging.DEBUG, filemode="w")


from .config import OUT_PATH
from .submodules.utilities.util import del_outputs, print_time
from .parser.list_x4files import list_entries_from_df
from .parser.exfor_entry import Entry, get_entry_update_date
from .parser.exfor_subentry import Subentry



## get update data from git commit and store info to Python dictionary
update_date = get_entry_update_date()

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

    try:
        entry_json["histories"] = sub.parse_main_history_dict()
    except:
        entry_json["histories"] = []

    entry_json["bib_record"] = sub.parse_main_bib_dict()
    entry_json["reactions"] = {}
    entry_json["data_tables"] = {}
    entry_json["experimental_conditions"] = {}

    for subent in entry.subents_nums:
        sub = Subentry(subent, entry.entry_body[subent])

        entry_json["experimental_conditions"][subent] = {}
        entry_json["data_tables"][subent] = {}

        # Extra information from BIB
        entry_json["experimental_conditions"][subent] = sub.parse_extra_bib_dict()

        ## REACTION
        if subent != "001":
            entry_json["reactions"][subent] = sub.parse_reaction_dict()

        ## COMMON
        entry_json["data_tables"][subent]["common"] = sub.parse_common()

        ## DATA
        if subent != "001":
            entry_json["data_tables"][subent]["data"] = sub.parse_data()


    return entry_json




def main(entnum):

    start_time = print_time()
    logging.info(f"Start processing {start_time}")

    try:
        entry_json = convert_exfor_to_json(entnum)
        write_dict_to_json(entnum, entry_json)

    except:
        logging.error(f"ERROR: at ENTRY: {entnum}")

    logging.info(f"End processing {print_time(start_time)}")


if __name__ == "__main__":
    ent = list_entries_from_df()
    # entries = random.sample(ent, len(ent))
    entries = ent
    for entnum in entries:
        print(entnum)
        main(entnum)

