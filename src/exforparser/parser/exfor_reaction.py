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
from pyparsing import *
from .exfor_field import parentheses, operators_dict


def split_sf(sf49):
    if sf49:
        return {
            "sf4": len(sf49) > 0 and sf49[0] or None,
            "sf5": len(sf49) > 1 and sf49[1] or None,
            "sf6": len(sf49) > 2 and sf49[2] or None,
            "sf7": len(sf49) > 3 and sf49[3] or None,
            "sf8": len(sf49) > 4 and sf49[4] or None,
            "sf9": len(sf49) > 5 and sf49[5] or None,
        }


def parse_primitive_reaction(reaction_field) -> dict:
    for pointer, p_block in reaction_field.items():
        flat_reaction = "".join(p_block)
        # a = parentheses.parse_string(flat_reaction)
        # b = free_text.parse_string("".join(p_block))
        return parentheses.parse_string(flat_reaction)


def parse_parenthesis(expr, ofs):
    pos_left = []
    pos_right = []
    count_left = 0
    count_right = 0

    while ofs < len(expr):

        if expr[ofs] == "(":
            count_left += 1
            pos_left += [ofs]

        if expr[ofs] == ")":
            count_right += 1
            pos_right += [ofs]

        ofs += 1
        if count_left == count_right:
            break

    assert len(pos_left) == len(pos_right)
    return pos_left, pos_right


def parse_nuclide(expr) -> list:
    m = re.match("\d{2}-[A-Z]{2}-[A-Z0-9]+(?:-[A-Z0-9]+)?", expr)
    return expr[m.start() : m.end()]


def parse_reaction_parts(x4_code) -> dict:
    opend = []
    closed = []
    pairs = []

    OPEN = False
    CLOSE = False

    for i in range(len(x4_code)):
        if x4_code[i] == "(":
            opend += [i]
            OPEN = True

        elif x4_code[i] == ")":
            closed += [i]
            CLOSE = True

        if x4_code[i] == ",":
            pass

        if OPEN and CLOSE:
            pairs += [[opend[-1], closed[-1]]]
            opend.pop()

        CLOSE = False

    reaction_dict = {
        "target": x4_code[1 : pairs[0][0]],
        "process": x4_code[pairs[0][0] + 1 : pairs[0][1]],
        "sf49": x4_code[pairs[0][1] + 1 : -1],
    }
    reaction_dict.update(split_sf(x4_code[pairs[0][1] + 1 : -1].split(",")))

    return reaction_dict


def get_details(bb) -> dict:
    if len(bb) == 3:
        sf49 = bb[2]
    else:
        sf49 = ",".join(
            [
                b.replace(",", "") if type(b) is not list else "(" + b[0] + ")"
                for b in bb[2:]
            ]
        )

    dict = {
        "target": bb[0],
        "process": bb[1][0],
        "sf49": sf49,
    }
    dict.update(split_sf(sf49.split(",")))
    return dict


def parse_operators(expr) -> list:
    """
    Return example: [{'operator': '/', 'span': [33, 34], 'main': False}, {'operator': '//', 'span': [64, 66], 'main': True}, {'operator': '/', 'span': [99, 100], 'main': False}] for the following example:
    (((92-U-233(N,F)ELEM/MASS,CUM,FY)/(92-U-233(N,F)42-MO-99,CUM,FY))//((92-U-235(N,F)ELEM/MASS,CUM,FY)/(92-U-235(N,F)42-MO-99,CUM,FY)))
    """
    return [
        {
            "operator": m.group(0).replace(")", "").replace("(", ""),
            "span": [m.start() + 1, m.end() - 1],
            "main": True if any(t in m.group(0) for t in ("//", "=")) else True if any(t in m.group(0) for t in ( "/", "*" )) else False,
        }
        for m in re.finditer(r"\)(?:[*+-/=]{1,2})\(|\)\)(?:[*+-/=]{1,2})\(", expr)
    ]

def parse_div_multi_operators(expr) -> list:
    return [
        {
            "operator": m.group(0).replace(")", "").replace("(", ""),
            "span": [m.start() + 1, m.end() - 1],
            "main": True if any(t in m.group(0) for t in ( "/", "*" )) else False,
        }
        for m in re.finditer(r"\)(?:[*/]{1})\(|\)\)(?:[*/]{1})\(", expr)
    ]



def math_same_operator(type, main_operator, operators, reaction_elements):
    if type == "before":
        mathJ = [
            [operators_dict[operators[0]["operator"]]] + [
            re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')', r["code"]) )
            for r in reaction_elements
            if r["span"][1] <= main_operator[0]["span"][0] ]
        ]
    elif type == "after":
        mathJ = [
            [operators_dict[operators[0]["operator"]]] + [
            re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')', r["code"]) )
            for r in reaction_elements
            if main_operator[0]["span"][1] <= r["span"][0] ]
        ]
    return mathJ


def math_some_operations(type, main_operator, op, reaction_elements):
    # sub_operator = [o for o in op if o["operator"] in ["/", "*"]]
    if type == "before":
        mathJ = [ 
            [operators_dict[op["operator"]]] 
            + 
            [
                re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')', r["code"]) )
                for r in reaction_elements
                if r["span"][1] <= main_operator[0]["span"][0]
            ] 
            ]
    elif type == "after":
        mathJ = [ 
            [operators_dict[op["operator"]]] 
            + 
            [
                re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')', r["code"]) )
                for r in reaction_elements
                if main_operator[0]["span"][1] <= r["span"][0] 
            ] 
            ]
    return mathJ



def parse_reaction(reaction_field) -> dict:
    reaction_info = {}
    dict = {}
    # print(reaction_field)
    for pointer, p_block in reaction_field.items():

        flat_reaction_str = "".join(p_block)

        ## parse locations of parentheses to separate code and free text
        l, r = parse_parenthesis(flat_reaction_str, 0)

        x4_code = flat_reaction_str[l[0] : r[-1] + 1]
        free_text = flat_reaction_str[r[-1] + 1 :]
        # print("EXFOR Reaction Code:", x4_code)

        """
        Parse operator (e.g. ')/(', ')//(', ')+('..etc ) and their positions in the EXFOR REACTION string
        It returns the list of dictionaries, e.g., 
            [{'operator': '+', 'span': [39, 40], 'main': False}, 
             {'operator': '/', 'span': [83, 85], 'main': False}]
        """
        operators = parse_operators(x4_code)
        

        if operators and x4_code.startswith("(("):
            # print("# All operators: ", operators)
            b = []
            mathJ = []
            reaction_elem = []

            """
            separate reaction code by operator's position
            operator_pos is a list of lists of spans of operators, e.g. [[39, 40], [76, 79], [116, 117]]
            """
            operator_pos = [o["span"] for o in operators]

            for i in range(len(operator_pos) + 1):
                span = []
                if i == 0:
                    span = [0, operator_pos[i][0]]
                    reaction_elem += [
                        {"span": span, "code": re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')', x4_code[span[0] : span[1]] ) ) }
                    ]

                elif i != len(operator_pos):
                    span = [operator_pos[i - 1][1], operator_pos[i][0]]
                    reaction_elem += [
                        {"span": span, "code": re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')',  x4_code[span[0] : span[1]] ) ) }
                    ]

                else:
                    span = [operator_pos[i - 1][1], len(x4_code)]
                    reaction_elem += [
                        {"span": span, "code": re.sub(r'[\(]{2,3}', '(', re.sub(r'[\)]{2,3}', ')', x4_code[span[0] : span[1]] ) )}
                    ]

            ## Check if the number of elements parsed are +1 than operators
            assert len(operators) + 1 == len(reaction_elem)


            if all(operators[0]["operator"] == x["operator"] for x in operators):
                """
                For the simple cases, where the all operators are the same or only one operator exits, such as:
                G0022: ((78-PT-198(G,N)78-PT-197,,SIG,,BRA)/(79-AU-197(G,N)79-AU-196,,SIG,,BRA))
                    --> ['Divide', '(78-PT-198(G,N)78-PT-197,,SIG,,BRA)', '(79-AU-197(G,N)79-AU-196,,SIG,,BRA)']
                10214: ((46-PD-106(N,X)45-RH-105,,SIG)+(46-PD-105(N,P)45-RH-105,,SIG,,RAB)+(46-PD-108(N,A)44-RU-105,,SIG,,RAB))
                    --> ['Add', '(46-PD-106(N,X)45-RH-105,,SIG)', '(46-PD-105(N,P)45-RH-105,,SIG,,RAB)', '(46-PD-108(N,A)44-RU-105,,SIG,,RAB)']
                10375: ((83-BI-209(N,EL)83-BI-209,,DA)//(83-BI-209(N,EL)83-BI-209,,DA))
                    --> ['Ratio', '(83-BI-209(N,EL)83-BI-209,,DA)', '(83-BI-209(N,EL)83-BI-209,,DA)']
                30076: ((26-FE-0(N,INL)26-FE-0,PAR,SIG)=(26-FE-56(N,INL)26-FE-56,PAR,SIG,,A))
                    --> ['Equal', '(26-FE-0(N,INL)26-FE-0,PAR,SIG)', '(26-FE-56(N,INL)26-FE-56,PAR,SIG,,A)']
                C0884: ((13-AL-27(A,X)1-H-1,,SIG)+(13-AL-27(A,X)1-H-2,,SIG)+(13-AL-27(A,X)1-H-3,,SIG)+(13-AL-27(A,X)2-HE-3,,SIG)+(13-AL-27(A,X)2-HE-4,EM,SIG))
                    --> ['Add', '(13-AL-27(A,X)1-H-1,,SIG)', '(13-AL-27(A,X)1-H-2,,SIG)', '(13-AL-27(A,X)1-H-3,,SIG)', '(13-AL-27(A,X)2-HE-3,,SIG)', '(13-AL-27(A,X)2-HE-4,EM,SIG)']
                """
                mathJ = [operators_dict[operators[0]["operator"]]] + [
                    r["code"].replace("((", "(").replace("))", ")")
                    for r in reaction_elem
                ]

            elif not all(operators[0]["operator"] == x["operator"] for x in operators):
                """
                Search main operator, i.e. "//" and "=" from the list of operators
                It returns a list of the dictionary 
                    e.g. [{'operator': '//', 'span': [76, 79], 'main': True}] 
                if exists
                """
                main_operator = [o for o in operators if o["main"]]
                # print( "   # Main operator : ", main_operator)

                # sub_operator = parse_div_multi_operators(x4_code)
                # print( "   # Sub operator  : ", sub_operator)

                if main_operator:
                    """
                    If there are reaction elements before and/or after the main operator, which are "=" or "//", then
                    try to separate them and detect if there is another operator(s) among the elements separated by the main operator.
                    This is for the cases like follow:
                    30170: ((54-XE-0(N,G),,SPC,,MXW/REL)=(54-XE-129(N,G)54-XE-130,,SPC,,A/MXW/REL)+(54-XE-131(N,G)54-XE-132,,SPC,,A/MXW/REL))
                    C2768: (((2-HE-4(42-MO-100,N)44-RU-103,,SIG,,AV)+(2-HE-4(42-MO-100,2N)44-RU-102,,SIG,,AV))=((42-MO-100(A,N)44-RU-103,,SIG,,AV)+(42-MO-100(A,2N)44-RU-102,,SIG,,AV)))
                    O0577: (((92-U-0(P,F)51-SB-127,,SIG)+(92-U-0(P,F)50-SN-127-M,CUM,SIG))/(92-U-0(P,F)51-SB-122,,SIG))
                    """
                    mathJ += [operators_dict[main_operator[0]["operator"]]]
                    op_before = []
                    op_after = []

                    ## Children operators
                    for o in operators:
                        if o["span"][0] < main_operator[0]["span"][0]:
                            op_before += [o]

                        elif o["span"][0] > main_operator[0]["span"][1]:
                            op_after += [o]

                    if not op_before:
                        ## Add first reaction element before main operator
                        mathJ += [
                            re.sub(r'[\(]{2,3}', '(', r["code"])
                            for r in reaction_elem
                            if r["span"][1] <= main_operator[0]["span"][0]
                        ]

                    else:
                        """
                        The case if there is another operator before the main operator, such as:
                        C2768: (((2-HE-4(42-MO-100,N)44-RU-103,,SIG,,AV)+(2-HE-4(42-MO-100,2N)44-RU-102,,SIG,,AV))=((42-MO-100(A,N)44-RU-103,,SIG,,AV)+(42-MO-100(A,2N)44-RU-102,,SIG,,AV)))
                        """
                        if all(op_before[0]["operator"] == ob["operator"] for ob in op_before):
                            ## Check if the all operators in front of main operator are same (or only one operator)
                            mathJ +=  math_same_operator("before", main_operator, op_before, reaction_elem)

                        else:
                            for op in op_before:
                                mathJ +=  math_some_operations("before", main_operator, op, reaction_elem) 

                    if op_after:
                        if all(op_after[0]["operator"] == of["operator"] for of in op_after):
                            mathJ +=  math_same_operator("after", main_operator, op_after, reaction_elem)

                        else:
                            for of in op_after:
                                mathJ +=  math_some_operations("after", main_operator, of, reaction_elem) 


                    if not op_after:
                        ## Add last reaction element
                        mathJ += [
                            re.sub(r'[\(]{2,3}', '(', r["code"])
                            for r in reaction_elem
                            if main_operator[0]["span"][1] <= r["span"][0]
                        ]


                else:
                    """
                    This is for the cases like follows involving only with addition and substraction:
                    O0577: (((92-U-0(P,F)51-SB-127,,SIG)+(92-U-0(P,F)50-SN-127-M,CUM,SIG))/(92-U-0(P,F)51-SB-122,,SIG))
                    """
                    mathJ = [operators_dict[operators[0]["operator"]]] + [
                    r["code"].replace("((", "(").replace("))", ")")
                    for r in reaction_elem
                ]

            else:
                # mathJ = [operators_dict[ main_operator[0]["operator"] ]]
                mathJ += [r["code"] for r in reaction_elem]
                # print(mathJ)

            # print("  -> Math JSON:", mathJ)

            reaction_info = {
                "x4_code": x4_code,
                "children": [{**{"x4_code": r["code"]}, **parse_reaction_parts(r["code"])} for r in reaction_elem],
                "math_expression": mathJ,
                "operator": mathJ[0],
                "free_text": free_text,
            }

        else:
            reaction_info = {
                "x4_code": x4_code,
                "math_expression": [],
                "children": [
                    parse_reaction_parts(x4_code)
                ],
                "operator": [],
                "free_text": free_text,
            }
            reaction_info["children"][0].update({"operator": [], "x4_code": x4_code})

        reaction_info["pointer"] = pointer
        dict[pointer] = reaction_info

    return dict

