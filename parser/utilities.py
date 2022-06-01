####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
# 
# Disclaimer: The code is still under developments and not ready 
#             to use. It has beeb made public to share the progress
#             between collaborators. 
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import re
import itertools
import json
import time
import os
import pandas as pd


def corr(invalue):
    if re.search(r"\d|\.[+]\d", invalue):
        # invalue = invalue.replace("+", "E+")
        invalue = re.sub(r"(\d|\.)([+])(\d)", r"\1E+\3", invalue)
    if re.search(r"\d|\.[-]\d", invalue):
        # invalue = invalue.replace("-", "E-")
        invalue = re.sub(r"(\d|\.)([-])(\d)", r"\1E-\3", invalue)
    return invalue


def extract_key(v):
    return v[0]


def combine_dict(d1, d2):
    return {
        k: list(d[k] for d in (d1, d2) if k in d)
        for k in set(d1.keys()) | set(d2.keys())
    }


def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def flatten_list(list):
    # https://geekflare.com/flatten-list-python/
    # flat_list = itertools.chain(*list)
    return itertools.chain(*list)


def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def is_pointer(dict, key):
    if len(dict[key].keys()) == 1:
        return False
    else:
        return True


ELEMS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
    "112",
    "113",
    "114",
    "115",
    "116",
    "117",
    "118",
    "119",
    "120",
]


def ztoelem(z):
    if z == 0:
        elem_name = "n"
    else:
        try:
            z = z - 1
            elem_name = ELEMS[z]
        except ValueError:
            elem_name = ""
    # print(elem_name.capitalize())
    # return elem_name.upper()
    return elem_name.capitalize()


def elemtoz(elem):
    try:
        z = ELEMS.index(elem)
        z = z + 1
        z = str(z).zfill(3)
    except ValueError:
        z = ""
    return z


def numtoisomer(num):
    if num == "0":
        return "G"
    elif num == "1":
        return "M1"
    elif num == "2":
        return "M2"
    elif num == "3":
        return "M3"

def conv_unit(value, factor):
    return value * factor



def process_time(func):
    '''
    for debugging purpose, delete @decorator
    '''
    def inner(*args):
        start_time = time.time()
        func(*args)
        print(str(func), "--- %s seconds ---" % (time.time() - start_time))
    return inner


def del_outputs(name):
    import shutil
    import os
    from path import OUT_PATH

    path = os.path.join(OUT_PATH, name)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)



def rescue(processed):
    lines = []
    if os.path.exists("processed.dat"):
        with open("processed.dat") as f:
            lines = f.readlines()
        if processed in "".join(lines):
            return True

        else:
            with open(r"processed.dat", "a") as fp:
                fp.write(processed + "\n")
            return False

    else:
        with open(r"processed.dat", "a") as fp:
            fp.write(processed + "\n")
            return False



def reaction_to_mtmf(process, sf5, sf6):
    print(process, sf5, sf6)


def show_df_option():
    pd.reset_option("display.max_columns")
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1200)
