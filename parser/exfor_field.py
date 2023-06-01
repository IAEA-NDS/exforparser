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

from pyparsing import *


capitals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
special_chars = "@#\":,.;+-*/'<> _^%$()&!?$*~="

main_identifiers = [
    "TITLE",
    "AUTHOR",
    "INSTITUTE",
    "REFERENCE",
    "FACILITY",
]  # , "HISTORY"]
identifiers = [
    "ANALYSIS",
    "ADD-RES",
    "ASSUMED",
    "CORRECTION",
    "COVARIANCE",
    "COMMENT",
    "CRITIQUE",
    "DECAY-DATA",
    "DECAY-MON",
    "DETECTOR",
    "EN-SEC",
    "EXP-YEAR",
    "ERR-ANALYS",
    "FACILITY",
    "FLAG",
    "HALF-LIFE",
    "INC-SOURCE",
    "INC-SPECT",
    "LEVEL-PROP",
    "METHOD",
    "MISC-COL",
    "MONIT-REF",
    "MONITOR",
    "MOM-SEC",
    "PART-DET",
    "RAD-DET",
    "REL-REF",
    "RESULT",
    "SAMPLE",
    "STATUS",
]

columndef = [
    "id",
    "entry",
    "subentry",
    "pointer",
    "np",
    "year",
    "author",
    "min_inc_en",
    "max_inc_en",
    "points",
    "target",
    "process",
    "sf4",
    "residual",
    "sf5",
    "sf6",
    "sf7",
    "sf8",
    "sf9",
    "x4_code",
]
# FLAG COMMENT HISTORY STATUS EXP-YEAR CRITIQUE MISC-COL ADD-RES MOM-SEC  RESULT SAMPLE


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


def parse_double_parentheses(expr, end_pos):
    positions = []
    pos = 0

    while pos < end_pos:
        if any(x in expr[pos - 1] + expr[pos] for x in ("((", "))")):
            positions += [pos]

        pos += 1
        if pos == end_pos:
            break

    return positions


def parse_operator(expr, end_pos):
    positions = []
    pos = 0

    while pos < end_pos:
        if any(x in expr[pos - 1] + expr[pos] for x in (")*", ")/", ")+", ")-")):
            positions += [pos]

        pos += 1
        if pos == end_pos:
            break

    return positions


""" general expression """
ParserElement.set_default_whitespace_chars("\t")
# use after general colum parse


""" parse nested expression """
allowed_symbols = "=-+/,*. '"
thecontent = Word(alphanums + allowed_symbols)
parentheses = nestedExpr("(", ")", content=thecontent)
free_text = parentheses.suppress() + rest_of_line()


# nuclide format: 63-EU-151
nuclide = Combine(
    Word(nums)
    + Literal("-")
    + Word(alphas)
    + Literal("-")
    + Word(nums + alphas + allowed_symbols)
)


""" DATA - parse could cause error when DATA section has line break wiyh
no data"""
head_str = Word(capitals + "q" + nums + "-+/\* ", exact=11) | Word(
    capitals + "q" + nums + "-+/\* "
)
data_header = OneOrMore(head_str)

data_str = (
    White(" ", exact=11)
    | Word(" " + nums + "+-.eEdD", exact=11)
    | Word(" " + nums + "+-.eEdD")
)
data_body = data_str.leaveWhitespace() + ZeroOrMore(data_str.leaveWhitespace())
