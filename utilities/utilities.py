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
