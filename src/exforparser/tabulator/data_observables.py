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
###################################################################
import pandas as pd
import numpy as np

from exforparser.sql.stored import list_of_target, list_of_reactions_and_entries, observable_data_query, data_query_by_id
from exforparser.submodules.utilities.util import del_outputs, closest, slices

from .data_dir_files import get_thermal_dir_name, get_thermal_filename
from .data_write import write_to_thermal_table, write_to_resonance_spacing_table
from .exfor_reaction_mt import sf3_dict, sig_sf5
from .data_filter import filter_cross_section_case, filter_partial_cross_section_case
from .data_process import process_cross_section_case, process_partial_cross_section_case
import logging

pd.set_option('display.max_rows', None, 'display.max_columns', None)
pd.set_option('display.width', 2000, 'max_colwidth', None)


def crosssection():
    type = "xs"

    target_dict = list_of_reactions_and_entries(type)
    """
    return example:
    target_dict = {
        ....
        '95-AM-244-M': {'N,F': ['14047-005-0']}, 
        '96-CM-240': {'N,F': ['14229-014-0']}, 
        '96-CM-241': {'N,F': ['14229-015-0']}, 
        '96-CM-242': {'N,F': ['40597-002-0', '23076-004-0', '14229-016-0', '12496-008-0', '12991-002-0', '20881-019-0', '40779-007-0'], 
                    'N,G': ['22941-005-0', '22941-017-0', '22941-018-0', '20881-018-0']},
        }
    """
    # print(target_dict)
    # target_dict = {'1-H-D2O': {'N,G': ['20460-003-0']} }
    # target_dict = {"13-AL-27": {"N,INL": ['41323-009-0']}}
    # target_dict = {"12-MG-24": {"N,G": ['13544-002-0']}}
    # target_dict = {"6-C-12": {"N,A": ['14711-002-0']}}

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            # print(target, reaction, entries)
            for ent in entries:
                print(target, reaction, ent)
                entry_json = {}
                df = data_query_by_id(type, [ent])
                # print(df)
                if df.empty:
                    continue

                react_dict = df.iloc[0].to_dict()

                if filter_cross_section_case(react_dict, df):
                    continue

                entry_json["bib_record"] = {"first_author": react_dict["first_author"].split(".")[-1], 
                                            "year": react_dict["year"],
                                            "first_author_institute": react_dict["first_author_institute"],
                                            "main_facility_institute": react_dict["main_facility_institute"],
                                            "main_facility_type": react_dict["main_facility_type"],
                                            "main_reference": react_dict["main_reference"]
                                            }
                # print(df)
                try:
                    if react_dict["sf5"] is None or any(
                            sf5 == react_dict["sf5"] for sf5 in sig_sf5.keys()
                        ):
                        process_cross_section_case(df, react_dict["entry_id"], entry_json, react_dict)

                    if react_dict["sf5"] == "PAR":
                        ## none of (N,NON) PAR,SIG are useful
                        if filter_partial_cross_section_case(react_dict, df):
                            continue
                        process_partial_cross_section_case(df, react_dict["entry_id"], entry_json, react_dict)

                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except:
                    logging.error(f"ERROR: at {target_dict}", exc_info=True)
            

def thermal(type):
    thermal_data_reaction = ["N,TOT", "N,G", "N,P", "N,A", "N,EL", "N,F"]
    targets = list_of_target(type)

    # targets = ["13-AL-27", "11-NA-23", "23-V-51", "4-BE-7", "17-CL-35", "27-CO-59", "92-U-235"]
    # del_outputs(os.path.join(OUT_PATH, "thermaldata"))

    for target in targets:
        for reaction in thermal_data_reaction:
            # df = thermal_xs(target, reaction)
            df = observable_data_query(type, target, reaction)
            # print(df.sort_values(by="sf4"))
            for prod in df["sf4"].unique():
                react_dict = {"target": target, "process": reaction, "sf4": prod}

                if prod is None:
                    df2 = df[df["sf4"].isnull()]

                else:
                    df2 = df[df["sf4"] == prod]

                if df2.empty:
                    continue

                else:
                    if type == "thermal":
                        dir = get_thermal_dir_name("thermaldata/thermal_xs", react_dict)
                        outfile = get_thermal_filename(dir, react_dict)

                        write_to_thermal_table(type, dir, outfile, react_dict, df2)
    return



def read_ripl3_d0():
    # Z = El = A = Io = Bn = D0 = dD = S0 = dS = Gg = dG = Com = []
    path = "/Users/okumuras/Dropbox/Development/exforparser/examples/resonances_0.ripl3"
    df = pd.read_fwf(path, sep='\s+', comment='#', names=["Z", "El", "A", "Io", "Bn", "D0", "dD", "S0", "dS", "Gg", "dG", "Com."], dtype = {"Gg": np.float64, "dG": np.float64}, colspecs='infer')
    return df



def read_ripl3_d1():
    path = "/Users/okumuras/Dropbox/Development/exforparser/examples/resonances_1.ripl3"
    df = pd.read_fwf(path, sep='\s+', comment='#', names=["Z", "El", "A", "Io", "Bn", "D1", "dD", "S1", "dS", "Gg", "dG", "Com."], dtype = {"Gg": np.float64, "dG": np.float64}, colspecs='infer')
    return df


def resonance_spacing():
    """
    To extract the resonance spacing (N,0),,D reactions for Arjan Koning
    """
    type = "resonance_spacing"
    targets = list_of_target(type)

    ripl_d0 = read_ripl3_d0()
    ripl_d1 = read_ripl3_d1()


    for target in targets:
        reactions = ["N,0", "N,EL"]
        for reaction in reactions:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            z = target.split("-")[0]
            el = target.split("-")[1].title()
            a = target.split("-")[2]
            # print(z, el, a)
            df0 = ripl_d0[(ripl_d0["Z"] == int(z)) & (ripl_d0["El"] == el)  & (ripl_d0["A"] == int(a))]
            df1 = ripl_d1[(ripl_d1["Z"] == int(z)) & (ripl_d1["El"] == el)  & (ripl_d1["A"] == int(a))]

            dir = get_thermal_dir_name("average_parameters/resonance_spacing", react_dict)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_resonance_spacing_table(type, dir, outfile, react_dict, df, df0, df1)

    return



def resonance_integral():
    """
    To extract the resonance integral data, (N,G),,RI
    """
    reactions = ["N,TOT", "N,G", "N,P", "N,A", "N,ABS", "N,F", "N,SCT"]
    type = "resonance_integral"
    targets = list_of_target(type)

    for target in targets:
        for reaction in reactions:
            df = pd.DataFrame()
            print(target, reaction)
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            dir = get_thermal_dir_name("average_parameters/resonance_integral", react_dict)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_thermal_table(type, dir, outfile, react_dict, df)

    return




def macs():
    """
    To extract the Maxwellian average cross section, (N,x),,SIG,,MXW
    """
    reactions = ["N,G"]
    type = "macs"
    targets = list_of_target(type)
    for target in targets:
        for reaction in reactions:
            df = pd.DataFrame()
            print(target, reaction)
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            for i, row in df.groupby(["entry_id"], group_keys=False):

                if len(row) > 1:
                    ## if there are more than one incident energy close to 30 keV, select one of the closest
                    one_en = closest( row["en_inc"].unique(), 0.03 )
                    df = df.drop(df[ (df["entry_id"] == i[0] ) & ( df["en_inc"] != one_en ) ].index)

            dir = get_thermal_dir_name("average_parameters/macs", react_dict)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_thermal_table(type, dir, outfile, react_dict, df)

    return





def resonance_parameter():
    """
    To extract the resonance spacing (N,0),,D reactions for Arjan Koning
    """
    resonance_data_reaction = ["N,TOT", "N,G", "N,EL", "N,F"]
    type = "resonance_parameter"
    targets = list_of_target(type)
    print(reversed(targets))

    for target in reversed(targets):
        print(target)
        for reaction in resonance_data_reaction:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:  
                continue

        dir = get_thermal_dir_name("average_parameters/resonance_parameter", react_dict)
        outfile = get_thermal_filename(dir, react_dict)
        write_to_resonance_table

    return 



def gamma_gamma():
    """
    To extract the resonance spacing (N,0),,D reactions for Arjan Koning
    """
    resonance_data_reaction = [ "N,G" ]
    type = "gamma_gamma"
    targets = list_of_target(type)

    ripl_d0 = read_ripl3_d0()
    ripl_d1 = read_ripl3_d1()

    for target in targets:
        print(target)
        for reaction in resonance_data_reaction:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:  
                continue

            z = target.split("-")[0]
            el = target.split("-")[1].title()
            a = target.split("-")[2]
            # print(z, el, a)
            df0 = ripl_d0[(ripl_d0["Z"] == int(z)) & (ripl_d0["El"] == el)  & (ripl_d0["A"] == int(a))]
            df1 = ripl_d1[(ripl_d1["Z"] == int(z)) & (ripl_d1["El"] == el)  & (ripl_d1["A"] == int(a))]
            df0 = df0.drop(df0[df0["Gg"].isnull()].index)
            df1 = df1.drop(df1[df1["Gg"].isnull()].index)

            dir = get_thermal_dir_name("average_parameters/gamma_gamma", react_dict)
            outfile = get_thermal_filename(dir, react_dict)
            write_to_resonance_spacing_table(type, dir, outfile, react_dict, df, df0, df1)

    return 
        # write_to_resonance_spacing_table(dir, outfile, react_dict)




