import re
import itertools
import json


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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


import time
def process_time(func):
    '''
    for debugging purpose, delete @decorator
    '''
    def inner(*args):
        start_time = time.time()
        func(*args)
        print("--- %s seconds ---" % (time.time() - start_time))
    return inner


def del_outputs(name):
    import shutil
    import os
    from path import OUT_PATH

    path = os.path.join(OUT_PATH, name)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)



# def bib_general(field_body):
#     '''
#     field_body looks like
#     [[' ', '(1.) Thickness off 10.6 b/atom'], [' ', '(2.) Thickness off 28.8 b/atom'],
#     '''
#     previous_pointer = ''
#     after_text = []
#     x4code_str = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#     # x4code_str = {"None": {"None" : {"code":'', "freetext":''}}}

#     for _, val in enumerate(field_body):
#         pointer = val[0]

#         if previous_pointer == '':
#             previous_pointer = val[0] #str(val[0]).zfill(2)

#         if val[1].startswith("(("):# or val[1].endswith("/") or val[1].endswith("))"):
#             ''' catch double quated
#             e.g. DECAY-DATA ((1.)55-CS-138-M,2.9MIN,DG) (6-)-STATE.
#             '''
#             if pointer == ' ':
#                 pointer = 'NO-P'

#             ''' val[1][1:] means omitting the first parenthesis '''
#             flag = flagged.parse_string(val[1][1:])[0]

#             ''' exclude flag and get coded inside parenthesis '''
#             flag_code = double_flaggedcode.parse_string(val[1])

#             ''' free text after the code () '''
#             after_text = doubleflaged_after_text.parse_string(val[1])

#             ''' set value into dict '''
#             x4code_str[pointer][flag] = {"code": flag_code[0], "freetext" : after_text[0]}


#         elif val[1].startswith("(") and not val[1].startswith("(("):
#             ''' 2cases exist:
#                     case1: (1.) flag,
#                     case2: (53-I-130-G,12.36HR,DG) decay data
#             '''

#             if pointer == ' ':
#                 pointer = 'NO-P'

#             ''' catching case1 and case2 '''
#             try:
#                 flag = flagged.parse_string(val[1])[0]
#                 x4code = 'None'
#             except:
#                 x4code = x4codelike.parse_string(val[1])[0]
#                 flag = 'NO-FL'

#             x4code_str[pointer][flag]["code"] = x4code

#             ''' parse and append free text after the code '''
#             after_text = flaged_after_text.search_string(val[1])
#             if after_text:
#                 x4code_str[pointer][flag]["freetext"].append(after_text[0][0])

#         else: # free text only rows
#             # print ("pointer", pointer, "previous_pointer", previous_pointer)
#             flag = 'NO-FL'
#             if pointer == ' ' and previous_pointer != "":
#                 pointer = previous_pointer

#             x4code_str[pointer][flag]["freetext"].append(''.join(val[1]))

#         if pointer != ' ':
#             previous_pointer = pointer

#     # dict_filed = dict(x4code_str[0][0:])
#     dict_filed = dict(x4code_str)

#     print (dict_filed)

#     return dict_filed

# def bib_reactionlike(field_body):
#     '''
#     field_body looks like
#     [[' ', '(1.) Thickness off 10.6 b/atom'], [' ', '(2.) Thickness off 28.8 b/atom'],
#     '''
#     print(field_body)
#     previous_pointer = ''
#     after_text = []
#     x4code_str = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#     # x4code_str = {"None": {"None" : {"code":'', "freetext":''}}}

#     for _, val in enumerate(field_body):
#         pointer = val[0]

#         if previous_pointer == '':
#             previous_pointer = val[0] #str(val[0]).zfill(2)

#         if val[1].startswith("(("):# or val[1].endswith("/") or val[1].endswith("))"):
#             ''' catch double quated
#             e.g. DECAY-DATA ((1.)55-CS-138-M,2.9MIN,DG) (6-)-STATE.
#             '''
#             if pointer == ' ':
#                 pointer = 'NO-P'

#             ''' val[1][1:] means omitting the first parenthesis '''
#             monit = monitref.parse_string(val[1][1:])[0]

#             ''' exclude flag and get coded inside parenthesis '''
#             monit_code = double_monitrefrcode.parse_string(val[1])

#             ''' free text after the code () '''
#             after_text = doubleflaged_after_text.parse_string(val[1])

#             ''' set value into dict '''
#             x4code_str[pointer][monit] = {"code": monit_code[0], "freetext" : after_text[0]}
#             # print("here")

#         elif val[1].startswith("(") and not val[1].startswith("(("):
#             ''' only 1 cases exist:
#                     case2: MONITOR    (13-AL-27(N,A)11-NA-24,,SIG)
#             '''
#             monit = 'None'

#             if pointer == ' ':
#                 pointer = 'NO-P'

#             ''' catching case1 and case2 '''
#             try:
#                 x4code = reaction_code.parse_string(val[1])[0]
#             except:
#                 x4code = 'None'

#             x4code_str[pointer][monit]["code"] = x4code

#             ''' parse and append free text after the code '''
#             after_text = flaged_after_text.search_string(val[1])
#             if after_text:
#                 x4code_str[pointer][monit]["freetext"].append(after_text[0][0])

#         else: # free text only rows
#             # print ("pointer", pointer, "previous_pointer", previous_pointer)
#             flag = 'NO-FL'
#             if pointer == ' ' and previous_pointer != "":
#                 pointer = previous_pointer

#             x4code_str[pointer][monit]["freetext"].append(''.join(val[1]))

#         if pointer != ' ':
#             previous_pointer = pointer

#     # dict_filed = dict(x4code_str[0][0:])
#     dict_filed = dict(x4code_str)

#     print (dict_filed)

#     return dict_filed
