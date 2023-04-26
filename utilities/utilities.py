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
import shutil
import time
import json
import sys
import os
import re
import itertools
import json
import time
import os


sys.path.append("../")
from config import OUT_PATH, EXFOR_MASTER_REPO_PATH


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


def dict_merge(dicts_list):
    d = {**dicts_list[0]}
    for entry in dicts_list[1:]:
        # print("entry:", entry)
        for k, v in entry.items():
            d[k] = (
                [d[k], v]
                if k in d and type(d[k]) != list
                else [*d[k] + v]
                if k in d
                else v
            )
    return d


def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def check_list(init_list):
    print(init_list)
    # print(any(isinstance(i, list) for i in init_list))

    def _is_list_instance(init_list):
        print(isinstance(init_list, list))

        sub_list = flatten_list(init_list)
        _is_list_instance(sub_list)

        return isinstance(init_list, list)


def flatten(xs):
    from collections.abc import Iterable

    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def flatten_list(list):
    return [item for sublist in list for item in sublist]


def flatten_list_original(list):
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


def conv_unit(value, factor):
    return value * factor


def reaction_to_mtmf(process, sf5, sf6):
    print(process, sf5, sf6)


def slices(s, *args):
    position = 0
    for length in args:
        yield s[position : position + length]
        position += length


def del_file(fname):
    os.remove(fname)


def del_outputs(name):

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
            with open(r"processed_id.dat", "a") as fp:
                fp.write(processed + "\n")
            return False

    else:
        with open(r"processed_id.dat", "a") as fp:
            fp.write(processed + "\n")
            return False


def process_time(func):
    """
    for debugging purpose, delete @decorator
    """

    def inner(*args):
        start_time = time.time()
        func(*args)
        print(str(func), "--- %s seconds ---" % (time.time() - start_time))

    return inner


def print_time(start_time=None):
    if start_time:
        str = "--- %s seconds ---" % (time.time() - start_time)
        return str

    else:
        return time.time()


def get_entry_update_date():
    d = {}
    file = os.path.join(EXFOR_MASTER_REPO_PATH, "entry_updatedate.dat")
    with open(file) as f:
        for line in f:
            x = line.split(" ")
            d.update({x[0]: {"last_update": x[1], "revisions": x[2].strip()}})
    return d
