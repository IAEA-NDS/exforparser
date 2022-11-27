import re
from pyparsing import *

from .exfor_field import parse_parenthesis, parentheses


def get_block(subent_body, sec_name):
    """
    purpose: chop subent into section: BIB, COMMON, DATA blocks
    Input:
        subent_body: List that includes the SUBENT and ENDSUBENT rows
            e.g.
            ['SUBENT        32662005   20060621   20070213   20070209       3121', 'BIB                  2          2', 'REACTION   (92-U-238(N,F),,NU,,FIS,DERIV)', 'STATUS     (DEP,32662002) Data taken from text .', 'ENDBIB               2', 'NOCOMMON             0          0', 'DATA                 1          1', 'DATA', 'PRT/FIS', '2.75', 'ENDDATA              3', 'ENDSUBENT           10']
    Output:
        block_body: List
    """
    block_body = []
    data_rex = re.compile("^DATA\s+[0-9]+\s+[0-9]+")

    for line in subent_body:

        if line[0:10].strip() == "NO" + sec_name:  # if NOCOMMON etc
            block_body = ["NO" + sec_name]
            break

        elif (line[0:10].strip() == sec_name and sec_name != "DATA") or data_rex.match(
            line
        ):
            block_body = [line]

        elif line[0:10].strip() == "END" + sec_name:
            block_body += [line]
            break

        else:
            block_body += [line]

    return block_body


def parse_block_by_pointer_identifier(block_body) -> dict:
    """
    purpose: read block and transform to Python dictionary
    Input:
        block_body: List that includes the start and end rows
            e.g.
            ['BIB                  4          5', 'REACTION   (92-U-238(N,F)MASS,CHN,FY,,FIS)', 'ERR-ANALYS (DATA-ERR) description at Subent 001.', 'STATUS     (TABLE)', 'HISTORY    (20090820A) SD: keyword TABLE in STATUS was shifted', '                           to the right according to EXFOR rules', 'ENDBIB               5']
    Output:
        block_dict: Python dictionary pointer as a key
    """

    identifier = None

    block_dict = {}
    identifier_dict = {}

    pointer = 0
    body = []

    for line in block_body:
        ## if the row starts with identifier
        if not line[0:10].isspace():
            ####### indentifier
            if not identifier:
                ## for the first identifier case
                identifier = line[0:10].strip()
                body = [line[11:]]
                identifier_dict = {}

            else:
                ## For the identifiers of second and the subsequents
                ## finalize the last identifier and initialize for the next
                identifier_dict[pointer] = body
                block_dict[identifier] = identifier_dict

                ## clear previous identifier
                body = []
                identifier = None
                identifier_dict = {}

            ####### pointer
            if not line[10:11].isspace():
                pointer = line[10:11]

            else:
                pointer = 0

            ## assign new identifier
            identifier = line[0:10].strip()
            body = [line[11:]]

        else:
            ## Row without identifier
            if not line[10:11].isspace():
                if line[10:11] != pointer:

                    ## finalize the last identifier with pointer, and initialize next
                    identifier_dict[pointer] = body
                    body = []

                    ## assign new pointer
                    pointer = line[10:11]
                    body = [line[11:]]

            else:
                body += [line[11:]]

    return block_dict


def get_text_location_index(block, line_num, position):
    """
    Input:
        block: whole block of identifier-pointer
        line_num: line number
        position: last position where parenthese closed
    Output:
        i: line number (list index)
        l - position: text start position in the i_th line
    """

    l = 0
    i = 0

    for i in range(len(block)):
        if i < line_num:
            continue

        l += len(block[i])

        if l >= position:
            break

    return i, [len(block[i]) - (l - position)]


def get_identifier_details(identifier_block) -> list:
    """
    Input:
        bib_block: { pointer: [list of rows] }
                   e.g. {0: ['(VDG,3CPRBJG) 4.5 MV Van de Graaff']}
        identifier_block: only [list of rows]
    Output:
        identifier_set: list of dictionaries
            [{code, free_text}, {code, free_text}, {code, free_text}]
    """

    identifier_set = []
    small_dict = {}
    cont = False
    skip_p_line = False

    x = None
    f = []
    ii = 0

    for i in range(len(identifier_block)):
        line = identifier_block[i]

        if not skip_p_line:
            try:
                l_opens, r_closes = parse_parenthesis(line, 0)

            except:
                match = Located(parentheses).parse_string("".join(identifier_block[i:]))
                l_opens = [match[0]]
                ii, r_closes = get_text_location_index(identifier_block, i, match[-1])
                x = "".join(identifier_block[i:])[match[0] : match[-1]]
                # print("x4_code ends at line:", ii, "char:", r_closes)

                skip_p_line = True

        if i < ii:
            ## skip lines if the x4_code continues
            continue

        if l_opens and not skip_p_line:
            if l_opens[0] == 0:
                if cont:
                    ## finalize the previous code
                    small_dict = {"x4_code": x, "free_txt": f}
                    identifier_set += [small_dict]
                    ## clear previous free text lines
                    x = None
                    f = []
                    cont = False
                    small_dict = {}

                x = line[l_opens[0] : r_closes[-1] + 1]
                f = [line[r_closes[-1] + 1 :]] if line[r_closes[-1] + 1 :] != "" else []

                cont = True

            else:
                ## parensis somewhere in the free text
                f += [line]
                cont = True

        elif skip_p_line:
            f = [line[r_closes[-1] + 1 :]] if line[r_closes[-1] + 1 :] != "" else []
            small_dict = {"x4_code": x, "free_txt": f}
            identifier_set += [small_dict]

            skip_p_line = False
            cont = False
            continue

        else:
            f += [line]
            cont = True

        if i == len(identifier_block) - 1:
            ## finalize the dictionary at the last line
            small_dict = {"x4_code": x, "free_txt": f}
            identifier_set += [small_dict]

    return identifier_set
