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
from exforparser.config import OUT_PATH
from exforparser.submodules.utilities.util import del_outputs, print_time
from exforparser.parser.list_x4files import list_exfor_files, list_entries_from_pickle
from exforparser.parser.exfor_entry import Entry, get_entry_update_date
from exforparser.parser.exfor_subentry import Subentry
from exforparser.parser.exfor_bib import correct_pub_year


## get update data from git commit and store info to Python dictionary
update_date = get_entry_update_date()


def _fill_missing_references(entry_json: dict) -> None:
    """
    If SUBENT 001 has no REFERENCE field, collect references from the
    individual subentries and backfill bib_record["references"].

    Some EXFOR entries store REFERENCE only in non-001 subentries
    (e.g. each subentry cites its own publication).  Without this step
    the entry-level DB record would have main_reference=NULL and the
    output file headers would contain no citation.

    Deduplication is done by x4_code so the same journal paper is not
    listed twice even when it appears in multiple subentries.
    """
    if entry_json["bib_record"].get("references"):
        return  # 001 already has references — nothing to do

    seen: set = set()
    for subent, pointers in entry_json["experimental_conditions"].items():
        if subent == "001":
            continue
        for pointer, cond in pointers.items():
            for ref in cond.get("reference", []):
                x4_code = ref.get("x4_code")
                if not x4_code or x4_code in seen:
                    continue
                seen.add(x4_code)
                entry_json["bib_record"]["references"].append(
                    {
                        "x4_code": x4_code,
                        "free_txt": ref.get("free_txt", []),
                        "publication_year": correct_pub_year(x4_code),
                        "doi": None,
                        "pointer": pointer,
                    }
                )


def write_dict_to_json(entnum, dic):
    """
    bib info write into json file
    """
    dir = os.path.join(OUT_PATH, "exfor_json/json", entnum[:3])

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
    entry_json["last_updated"] = update_date.get(entnum, {}).get("last_update")
    entry_json["number_of_revisions"] = update_date.get(entnum, {}).get("revisions")

    try:
        entry_json["histories"] = sub.parse_main_history_dict()
    except Exception:
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

    _fill_missing_references(entry_json)
    return entry_json


def convert(entnum):
    entry_json = convert_exfor_to_json(entnum)
    write_dict_to_json(entnum, entry_json)


def convert_all():
    ent = []
    df = list_exfor_files()

    for _, row in df.iterrows():
        ent += [row["entry"]]

    # entries = random.sample(ent, len(ent))
    entries = ent

    start_time = print_time()
    logging.info(f"Start processing {print_time()}")

    for entnum in entries:
        print(entnum)
        # process(entnum)
        try:
            convert(entnum)
        except KeyboardInterrupt:
            print("CTR + C")
            break
        except Exception:
            logging.error(f"ERROR: at ENTRY: {entnum}", exc_info=True)

    logging.info(f"End processing {print_time()}")


def convert_updated_entry():
    ent = []
    old_df = list_entries_from_pickle()
    print(old_df)
    new_df = list_exfor_files()
    print(new_df)

    if old_df.equals(new_df):
        return

    # addtion, update
    df_diff = old_df.compare(new_df)

    for _, row in df_diff.iterrows():
        ent += [row["entry"]]


    logging.info(f"Start processing {print_time()}")

    for entnum in ent:
        print(entnum)
        # process(entnum)
        try:
            convert(entnum)
        except KeyboardInterrupt:
            print("CTR + C")
            break
        except Exception:
            logging.error(f"ERROR: at ENTRY: {entnum}", exc_info=True)

    logging.info(f"End processing {print_time()}")


if __name__ == "__main__":
    convert_all()
