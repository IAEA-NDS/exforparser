from logging import raiseExceptions
import pandas as pd
import os
import re
import json
import pickle
import matplotlib.pyplot as plt
from contextlib import redirect_stdout

from path import OUT_PATH
from exparser import convert_single
from parser.utilities import process_time, del_outputs
from parser.exfor_entry import Entry
from parser.exfor_subentry import Subentry,MainSubentry
from parser.exfor_data import get_inc_energy, get_colmun_indexes
from dictionary.exfor_dictionary import Diction


d = Diction()
en_heads = d.get_incident_en_heads()
en_heads_err = d.get_incident_en_err_heads()
data_heads = d.get_data_heads()
data_heads_err = d.get_data_err_heads()
mass_heads = d.get_mass_heads()
elem_heads = d.get_elem_heads()



def simple_xy(locs, data_dict, normalize_factor):
    x = []
    x_min = []
    x_max = []
    x_mean = []

    if data_dict and locs:
        for l in locs:

            factor = float(d.get_unit_factor(data_dict["units"][l])) / normalize_factor
            x = [p * factor if p is not None else None for p in data_dict["data"][str(l)]]
            
            if "-MIN" in data_dict["heads"][l]:
                x_min = x.copy()

            if "-MAX" in data_dict["heads"][l]:
                x_max = x.copy()
            
            if "-MEAN" in data_dict["heads"][l]:
                x_mean = x.copy()

        if x_min and x_max:
            x = [(min + max)/2 if min is not None else None if max is not None else None for min in x_min for max in x_max ]

        if x_mean:
            x = [n for n in x_mean for n in x if n != None] 

    return x


def table_out(id, dir, file, main_bib_dict, react_dict, df):

    ## create directory if it doesn't exist
    if os.path.exists(dir):
        pass
    else:
        os.makedirs(dir)

    ## always overwrite
    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print( 
                    "# entry       :", id[0:5], "\n"
                    "# subentry    :", id[5:8], "\n"
                    "# pointer     :", id[8:], "\n"
                    "# reaction    :", react_dict[id[8:]]["x4code"], "\n"
                    "# year        :", main_bib_dict["references"][0]["publication year"], "\n"
                    "# author      :", main_bib_dict["authors"][0]["name"], "\n"
                    "# institute   :", (main_bib_dict["institutes"][0]["x4code"] if main_bib_dict.get("institutes") else None), "\n"
                    "# reference   :", main_bib_dict["references"][0]["x4code"],"\n"
                    "# facilitie   :", (main_bib_dict["facilities"][0] if main_bib_dict.get("facilities") else None)
                )
                print("#     E(MeV)          dE(MeV)           xs(mb)           dxs(mb)           frame" )
                for i, row in df.iterrows():
                    print('{:17.5E}{:17.5E}{:17.5E}{:17.5E}       # {:22s}'.format(
                        row["x"], row["dx"], row["y"], row["dy"], row["Frame"]
                        )
                    )
        f.close()


def exfortableformat(entnum, subentnum, pointer):
    print("process: ", entnum, subentnum, pointer)
    entry = Entry(entnum)
    ## parse and save bib data
    main = MainSubentry("001", entry.entry_body["001"])
    sub = Subentry(subentnum, entry.entry_body[subentnum])
    id = entnum + subentnum + pointer
    ## just for a test
    # incident_energy = get_inc_energy(main, sub)

    ### generate output filename
    reac_dic = sub.parse_reaction()[pointer]

    dir = os.path.join(
        OUT_PATH,
        "exfortable",
        reac_dic["process"].split(",")[0].lower(),
        reac_dic["target"].split("-",1)[1].capitalize(),
        reac_dic["sf6"],
        reac_dic["process"].replace(",", "-").lower()
    )

    file = os.path.join(
        dir,
        (
            reac_dic["process"].split(",")[0].lower()
            + "_"
            + reac_dic["target"].split("-",1)[1].capitalize()
            + "_"
            + main.main_bib_dict["authors"][0]["name"].replace(" ", "")
            + "_"
            + main.main_bib_dict["references"][0]["publication year"]
            + "_"
            + id
            + "_"
            + "0"
            + ".dat"
        ),
    )

    factor_to_mev = 1.0e+6
    factor_to_milibarn = 1.0e-3

    ## x axsis data: EN, etc
    locs, data_dict = get_colmun_indexes(main, sub, en_heads)
    if not locs or not data_dict:
        print("skip to produce exfortable")
        return

    if data_dict and locs:
        x = []
        x_min = []
        x_max = []
        x_mean = []
        type = ""
        for l in locs:
            if "-CM" in data_dict["units"][l]:
                type = "Center-of-mass"

            elif "KT" in data_dict["units"][l]:
                type = "Spectrum temperature"
            
            elif "WVE-LN" in data_dict["units"][l]:
                type = "Wavelength"

            else:
                type = "Lab"

            factor = float(d.get_unit_factor(data_dict["units"][l])) / factor_to_mev
            x = [p * factor if p is not None else None for p in data_dict["data"][str(l)]]
            
            if "-MIN" in data_dict["units"][l]:
                x_min = x.copy()

            if "-MAX" in data_dict["units"][l]:
                x_max = x.copy()
            
            if "-MEAN" in data_dict["units"][l]:
                x_mean = x.copy()

        if x_min and x_max:
            x = [(min + max)/2 if min is not None else None if max is not None else None for min in x_min for max in x_max ]

        if x_mean:
            x = [n for n in x_mean for n in x if n != None] 

    ## dx axsis data: EN-ERR, etc
    locs, data_dict = get_colmun_indexes(main, sub, en_heads_err)
    dx = simple_xy(locs, data_dict, factor_to_mev)
    
    ## y axsis data: DATA etc    
    if pointer != "XX" and not None:
        data_heads_p = [h + " " * int(10-len(h)) + pointer for h in data_heads]
        locs, data_dict = get_colmun_indexes(main, sub, data_heads_p)
    else:
        locs, data_dict = get_colmun_indexes(main, sub, data_heads)
    if not locs or not data_dict:
        print("skip to produce exfortable")
        return
    y = simple_xy(locs, data_dict, factor_to_milibarn)

    ## dy axsis data: DATA-ERR etc
    if pointer != "XX" and not None:
        data_heads_err_p = [h + " " * int(10-len(h)) + pointer for h in data_heads_err]
        locs, data_dict = get_colmun_indexes(main, sub, data_heads_err_p)
    else:
        locs, data_dict = get_colmun_indexes(main, sub, data_heads_err)
    dy = simple_xy(locs, data_dict, factor_to_milibarn)

    # print(y, dy)
    # print(len(x), len(y), len(dx), len(dy))

    if x and y:
        if len(x) != len(y) and len(x) == 1:
            ## knowing x is a list not string
            x =  x  * len(y)

    if not dy:
        dy = [None] * len(y)

    if not dx:
        dx = [None] * len(y)

    if dx:
        if len(dx) != len(y) and len(dx) == 1:
            dx =  dx  * len(y)

    if dy:
        if len(dy) != len(y) and len(dy) == 1:
            dy =  dy  * len(y)

    # df = pd.DataFrame( {"id": id, "Frame": type, "x":x,  "y":y } )
    df = pd.DataFrame( {"id": id, "Frame": type, "x":x, "dx":dx, "y":y ,"dy":dy} ).fillna(0)
    # print(df)

    table_out(id, dir, file, main.main_bib_dict, sub.parse_reaction(), df)

    return df


@process_time
def main():
    try:
        df1 = pickle.load(open("pickle/reactions_0527.pickle", "rb"))
    except:
        raiseExceptions

    entry = "12515"
    target = "79-Au-197"
    process = "N,G"
    sf4 = "MASS"
    quantity = "SIG"
    sf8 = ["RES", "RTE", "SDT/AV", "SDT"]

    with pd.option_context("display.float_format", "{:11.3e}".format):
        df1 = df1[
        #     # (df1.entry == entry )
            (df1.target == target.upper())
            & (df1.process == process.upper()) 
            & (df1.sf5.isnull())
            & (df1.sf6 == quantity.upper())
            & (~df1.sf8.isin(sf8))
            & (df1.points > 0)
        #     # # & (df1.sf4 == sf4.upper())
                    ]
        print(df1.sort_values(by=["year","entry","subentry"]))

    df2 = pd.DataFrame()
    for i, row in df1.iterrows():
        convert_single(row["entry"], row["subentry"], row["pointer"])
        df = exfortableformat(row["entry"], row["subentry"], row["pointer"])
        df2 = pd.concat([df2, df])

    # print(df2)
    # # # df2[df2["x(MeV)"] <= 1e-6 ].plot(x ='x(MeV)', y='y(mb)', kind="scatter", logx=True, logy=True)
    df2.plot(x ="x", y="y", kind="scatter", logx=True, logy=True)
    plt.show()


if __name__ == "__main__":
    ## one sample run
    # df = exfortableformat("10341", "004", "XX") 
    # print(df)
    
    # del_outputs("json")
    # del_outputs("exfortable")
    main()



