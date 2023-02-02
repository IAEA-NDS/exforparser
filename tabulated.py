import random
import pandas as pd
import numpy as np
import logging


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logging.basicConfig(filename="tabulated.log", level=logging.DEBUG, filemode="w")

from config import OUT_PATH
from utilities.operation_util import del_outputs, print_time
from utilities.utilities import dict_merge
from exparser import convert_exfor_to_json, write_dict_to_json
from parser.list_x4files import good_example_entries, fpy_examples, list_entries_from_df
from parser.exfor_unit import unify_units
from tabulated.exfor_reaction_mt import mt_fy, rp_sig, mt_to_reaction, e_lvl_to_mt50

from tabulated.data_locations import *
from tabulated.data_write import *
from tabulated.data_dir_files import *
from tabulated.data_process import *

# initialize exfor_dictionary
from exfor_dictionary.exfor_dictionary import Diction
from utilities.ripl3_descretelevel import RIPL_Level


D = Diction()
## get possible heading list
x_en_heads = D.get_incident_en_heads()
x_en_err_heads = D.get_incident_en_err_heads()
x_data_heads = D.get_data_heads()
x_data_err_heads = D.get_data_err_heads()

mt_dict, sf3_dict = mt_to_reaction()
# print(sf3_dict)



def tabulated_to_exfortables_format(id, entry_json, data_dict_conv):
    entnum = id[0:5]
    subent = id[5:8]

    


    for pointer in entry_json["reactions"][subent]:
        id = entnum + subent + pointer
        print(id)

        if entry_json["reactions"][subent][pointer]["type"] is not None:
            ## if ratio or any other complex reactions, it will be skipped so far
            continue

        react_dict = entry_json["reactions"][subent][pointer]["children"][0]
        # print(react_dict)



        ## ------------------------  Case for the fission product yields ------------------------  ##
        if react_dict["sf6"] == "FY":
            if (
                not any(par == react_dict["sf5"] for par in mt_fy.keys())
                or any(
                    excep in react_dict["sf8"]
                    for excep in ("MSC", "REL", "FRC", "RES")
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue


            df = process_fy(pointer, react_dict, data_dict_conv)
            mt = mt_fy[react_dict["sf5"]]
            dir = get_dir_name(react_dict, mt)

            for en in df["en_inc"].unique():
                df2 = df[df["en_inc"] == en]
                filename = exfortables_filename_fy(
                    dir,
                    id,
                    mt_fy[react_dict["sf5"]],
                    en,
                    react_dict,
                    entry_json["bib_record"],
                )
                write_to_exfortables_format_fy(
                    id, dir, filename, entry_json["bib_record"], react_dict, df2
                )

        if react_dict["sf6"] == "AKE" or react_dict["sf6"] == "KE":
            df = process_sig(pointer, react_dict, data_dict_conv)
            mt = sf3_dict[react_dict["process"].split(",")[1]]["mt"]
            dir = get_dir_name(react_dict, mt)

            for en in df["en_inc"].unique():
                df2 = df[df["en_inc"] == en]
                filename = exfortables_filename_fy(
                    dir,
                    id,
                    mt,
                    en,
                    react_dict,
                    entry_json["bib_record"],
                )
                write_to_exfortables_format_sig(
                    id, dir, filename, entry_json["bib_record"], react_dict, df2
                )

        ## ------------------------  Case for the cross section measuements ------------------------  ##
        elif react_dict["sf6"] == "SIG":
            if (
                not any(
                    par == react_dict["process"].split(",")[1]
                    for par in sf3_dict.keys()
                )
                or any(
                    excep in react_dict["sf8"]
                    for excep in ["MSC", "REL", "FRC", "RES"]
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue


            if react_dict["sf5"] is None or any(sf5 == react_dict["sf5"] for sf5 in rp_sig.keys()):

                df = process_sig(pointer, react_dict, data_dict_conv)
                mt = sf3_dict[react_dict["process"].split(",")[1]]["mt"]
                dir = get_dir_name(react_dict, mt)

                if any(
                    r == react_dict["process"].split(",")[1]
                    for r in ("F", "TOT", "NON", "ABS")
                ) or (
                    react_dict["target"].split("-")[2] == "0"
                    and react_dict["sf4"] is None
                ):
                ## no reaction product would be given in these cases
                    filename = exfortables_filename_sig(
                        dir,
                        id,
                        sf3_dict[react_dict["process"].split(",")[1]]["mt"],
                        "NoProd",
                        react_dict,
                        entry_json["bib_record"],
                    )

                    write_to_exfortables_format_sig(
                        id, dir, filename, entry_json["bib_record"], react_dict, df
                    )

                else:
                    for prod in df["product"].unique():
                        df2 = df[df["product"] == prod]
                        filename = exfortables_filename_sig(
                            dir,
                            id,
                            sf3_dict[react_dict["process"].split(",")[1]]["mt"],
                            prod,
                            react_dict,
                            entry_json["bib_record"],
                        )
                        write_to_exfortables_format_sig(
                            id, dir, filename, entry_json["bib_record"], react_dict, df2
                        )


            elif react_dict["sf5"] == "PAR" and react_dict["process"].split(",")[1] == "INL":
                ## none of (N,NON) PAR,SIG are useful
                df = process_par_sig(pointer, react_dict, data_dict_conv)
                
                for e_lvl in df["e_outgoing"].unique():
                    df2 = df[df["e_outgoing"] == e_lvl]

                    if not react_dict["target"].split("-")[2] == "0":
                        L = RIPL_Level(react_dict["sf4"].split("-")[0], react_dict["sf4"].split("-")[2], e_lvl)
                        level_num = L.ripl_find_level_num()
                        mt = e_lvl_to_mt50(level_num)
                    else:
                        level_num = 0
                        mt = "99"

                    dir = get_dir_name(react_dict, mt)

                    filename = exfortables_filename_sig(
                        dir,
                        id,
                        mt,
                        "L" + str(level_num),
                        react_dict,
                        entry_json["bib_record"],
                    )
                    write_to_exfortables_format_par_sig(
                        id, dir, filename, entry_json["bib_record"], react_dict, df2
                    )

        ## ------------------------  Case for the angular distributions ------------------------  ##
        elif react_dict["sf6"] == "DA":
            if (
                not any(
                    par == react_dict["process"].split(",")[1]
                    for par in sf3_dict.keys()
                )
                or any(
                    react_dict["sf8"] != excep
                    for excep in ("EXP")
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue


            if react_dict["sf5"] is None or any(sf5 == react_dict["sf5"] for sf5 in rp_sig.keys()):

                df = process_sig(pointer, react_dict, data_dict_conv)
                mt = sf3_dict[react_dict["process"].split(",")[1]]["mt"]
                dir = get_dir_name(react_dict, mt)
                    
                for e in df["en_inc"].unique():
                    df2 = df[df["en_inc"] == e]

                    if react_dict["target"].split("-")[2] == "0" and react_dict["sf4"] is None:
                        filename = exfortables_filename_da(
                            dir,
                            id,
                            sf3_dict[react_dict["process"].split(",")[1]]["mt"],
                            e,
                            "NoProd",
                            react_dict,
                            entry_json["bib_record"],
                        )
                        write_to_exfortables_format_da(
                            id, dir, filename, entry_json["bib_record"], react_dict, df2
                        )

                    else:
                        for prod in df2["product"].unique():
                            df3 = df2[df2["product"] == prod]
                            filename = exfortables_filename_da(
                                dir,
                                id,
                                sf3_dict[react_dict["process"].split(",")[1]]["mt"],
                                e,
                                prod,
                                react_dict,
                                entry_json["bib_record"],
                            )
                            write_to_exfortables_format_da(
                                id, dir, filename, entry_json["bib_record"], react_dict, df3
                            )


            elif react_dict["sf5"] == "PAR" and react_dict["process"].split(",")[1] == "INL":
                ## none of (N,NON) PAR,SIG are useful
                df = process_par_sig(pointer, react_dict, data_dict_conv)
                
                for e_lvl in df["e_outgoing"].unique():
                    df2 = df[df["e_outgoing"] == e_lvl]


                    L = RIPL_Level(react_dict["sf4"].split("-")[0], react_dict["sf4"].split("-")[2], e_lvl)
                    level_num = L.ripl_find_level_num()
                    mt = e_lvl_to_mt50(level_num)
                    dir = get_dir_name(react_dict, mt)

                    filename = exfortables_filename_sig(
                        dir,
                        id,
                        mt,
                        "L" + str(level_num),
                        react_dict,
                        entry_json["bib_record"],
                    )
                    write_to_exfortables_format_par_da(
                        id, dir, filename, entry_json["bib_record"], react_dict, df2
                    )




def main():
    ent = list_entries_from_df()
    entries = random.sample(ent, len(ent))
    # entries = good_example_entries  + fpy_examples

    del_outputs(OUT_PATH + "exfortables/")

    start_time = print_time()
    logging.info(f"Start processing {start_time}")

    i = 0
    for entnum in entries:
        print(entnum)

        entry_json = convert_exfor_to_json(entnum)
        write_dict_to_json(entnum, entry_json)

        if entry_json.get("reactions"):
            pass
        else:
            continue

        common_main_dict = {}
        data_tables_dict = entry_json["data_tables"]
        data_dict = {}


        ## get SUBENT 001 COMMON block
        if data_tables_dict["001"].get("common"):
            common_main_dict = data_tables_dict["001"]["common"]

        ## looping over SUBENTRY from 002
        for subent in list(data_tables_dict.keys())[1:]:
            # print(entnum, subent)
            common_sub_dict = {}

            ## get SUBENT 002 COMMON block
            if data_tables_dict[subent].get("common"):
                common_sub_dict = entry_json["data_tables"][subent]["common"]

            ## get SUBENT 002 DATA block
            if data_tables_dict[subent].get("data"):
                data_dict = dict_merge(
                    [
                        common_main_dict,
                        common_sub_dict,
                        entry_json["data_tables"][subent]["data"],
                    ]
                )

                ## Unify units
                data_dict_conv = unify_units(data_dict)

                ## Unify data length
                data_dict_conv = data_length_unify(data_dict)
                # print(data_dict_conv["heads"])

            else:
                ## means there is NODATA defined in the Subent
                continue

            ## Most of the case pointers are related to the REACTIONs
            id = entnum + subent

            # tabulated_to_exfortables_format(id, entry_json, data_dict_conv)
            try:
                tabulated_to_exfortables_format(id, entry_json, data_dict_conv)
                # i += 1
                # if i > 1000:
                #     break
            except:
                logging.error(f"ERROR: at ENTRY: '{id}',")

    logging.info(f"End processing {print_time(start_time)}")


if __name__ == "__main__":
    main()
