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
    m = re.match(r"\d{2}-[A-Z]{2}-[A-Z0-9]+(?:-[A-Z0-9]+)?", expr)
    return expr[m.start() : m.end()] if m else None


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

    if not pairs:
        return {}

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
    # return [
    #     {
    #         "operator": m.group(0).replace(")", "").replace("(", ""),
    #         "span": [m.start() + 1, m.end() - 1],
    #         "main": (
    #             True
    #             if any(t in m.group(0) for t in ("//", "="))
    #             else True if any(t in m.group(0) for t in ("/", "*")) else False
    #         ),
    #     }
    #     for m in re.finditer(r"\)(?:[*+-/=]{1,2})\(|\)\)(?:[*+-/=]{1,2})\(", expr)
    # ]
    pattern = r"\)(?:(//)|(/)|(\*)|(\+)|(-)|(=))\("

    operators = []
    for m in re.finditer(pattern, expr):
        if m.group(1):
            op = "//"
        elif m.group(2):
            op = "/"
        elif m.group(3):
            op = "*"
        elif m.group(4):
            op = "+"
        elif m.group(5):
            op = "-"
        elif m.group(6):
            op = "="
        else:
            continue

        operators.append({
            "operator": op,
            "span": [m.start() + 1, m.end() - 1],
            "main": True if op in ("//", "=") else False
        })

    return operators



def parse_div_multi_operators(expr) -> list:
    return [
        {
            "operator": m.group(0).replace(")", "").replace("(", ""),
            "span": [m.start() + 1, m.end() - 1],
            "main": True if any(t in m.group(0) for t in ("/", "*")) else False,
        }
        for m in re.finditer(r"\)(?:[*/]{1})\(|\)\)(?:[*/]{1})\(", expr)
    ]


def build_math_operation(position, main_operator, operators, reaction_elements):
    """
    Build MathJSON substructure for operators before/after a main operator (//, =)
    Handles both same and mixed operators.
    """
    if not operators:
        return []

    same_op = all(operators[0]["operator"] == o["operator"] for o in operators)
    op = operators[0]

    subelements = [
        re.sub(r"[\(]{2,3}", "(", re.sub(r"[\)]{2,3}", ")", r["code"]))
        for r in reaction_elements
        if (r["span"][1] <= main_operator[0]["span"][0]
            if position == "before"
            else main_operator[0]["span"][1] <= r["span"][0])
    ]

    if same_op:
        return [operators_dict[op["operator"]]] + subelements
    else:
        # Mixed operators: produce list-of-lists, one entry per operator
        return [[operators_dict[o["operator"]]] + subelements for o in operators]



def math_same_operator(position, main_operator, operators, reaction_elements):
    """
    Compatibility wrapper kept for existing call sites.
    Delegates to build_math_operation.
    """
    return build_math_operation(position, main_operator, operators, reaction_elements)


def math_some_operations(position, main_operator, op, reaction_elements):
    """
    Compatibility wrapper for single operator entry (originally expected 'op' to be a single dict).
    Returns the structure for that single operator.
    """
    # wrap op into a single-element list and delegate
    return build_math_operation(position, main_operator, [op], reaction_elements)




def parse_reaction(reaction_field) -> dict:
    reaction_info = {}
    dict = {}

    for pointer, p_block in reaction_field.items():
        flat_reaction_str = "".join(p_block)
        l, r = parse_parenthesis(flat_reaction_str, 0)
        x4_code = flat_reaction_str[l[0]:r[-1] + 1]
        free_text = flat_reaction_str[r[-1] + 1:]
        operators = parse_operators(x4_code)

        if operators and x4_code.startswith("(("):
            reaction_elem = []
            operator_pos = [o["span"] for o in operators]

            for i in range(len(operator_pos) + 1):
                if i == 0:
                    span = [0, operator_pos[i][0]]
                elif i != len(operator_pos):
                    span = [operator_pos[i - 1][1], operator_pos[i][0]]
                else:
                    span = [operator_pos[i - 1][1], len(x4_code)]

                reaction_elem.append({
                    "span": span,
                    "code": re.sub(r"[\(]{2,3}", "(", re.sub(r"[\)]{2,3}", ")", x4_code[span[0]:span[1]])),
                })

            assert len(operators) + 1 == len(reaction_elem)

            # recursive helper for nested math expressions
            def build_math_expr(code):
                inner_ops = parse_operators(code)
                if not inner_ops:
                    return code

                if all(inner_ops[0]["operator"] == o["operator"] for o in inner_ops):
                    # same operator
                    inner_elems = []
                    op_pos = [o["span"] for o in inner_ops]
                    for i in range(len(op_pos) + 1):
                        if i == 0:
                            s = [0, op_pos[i][0]]
                        elif i != len(op_pos):
                            s = [op_pos[i - 1][1], op_pos[i][0]]
                        else:
                            s = [op_pos[i - 1][1], len(code)]
                        sub = code[s[0]:s[1]]
                        inner_elems.append(build_math_expr(sub))
                    return [operators_dict[inner_ops[0]["operator"]]] + inner_elems

                # find main operator (// or = or /)
                main_op = [o for o in inner_ops if o["main"]] or [o for o in inner_ops if o["operator"] in ("/", "*")]
                if not main_op:
                    return code
                m = main_op[0]
                before = code[:m["span"][0]]
                after = code[m["span"][1]:]

                return [
                    operators_dict[m["operator"]],
                    build_math_expr(before),
                    build_math_expr(after)
                ]

            mathJ = build_math_expr(x4_code)

            reaction_info = {
                "x4_code": x4_code,
                "children": [
                    {**{"x4_code": r["code"]}, **parse_reaction_parts(r["code"])}
                    for r in reaction_elem
                ],
                "math_expression": mathJ,
                "operator": mathJ[0] if isinstance(mathJ, list) else None,
                "free_text": free_text,
            }

        else:
            reaction_info = {
                "x4_code": x4_code,
                "math_expression": None,
                "children": [parse_reaction_parts(x4_code)],
                "operator": None,
                "free_text": free_text,
            }
            reaction_info["children"][0].update({"operator": None, "x4_code": x4_code})

        reaction_info["pointer"] = pointer
        dict[pointer] = reaction_info

    return dict

