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
]

ref_identifiers = [
    "REFERENCE",
    "MONIT-REF",
    "REL-REF",
]

experimental_condition_identifires = [
    "ANALYSIS",
    "ADD-RES",
    "ASSUMED",
    "CORRECTION",
    "COVARIANCE",
    "DECAY-DATA",
    "DECAY-MON",
    "DETECTOR",
    "EN-SEC",
    "ERR-ANALYS",
    "FACILITY",
    "FLAG",
    "HALF-LIFE",
    "INC-SOURCE",
    "INC-SPECT",
    "LEVEL-PROP",
    "METHOD",
    "MONITOR",
    "MOM-SEC",
    "PART-DET",
    "RAD-DET",
    "SAMPLE",
]

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

operators_dict = {
    "/": "Divide",
    "+": "Add",
    "-": "Subtract",
    "*": "Multiply",
    "//": "Ratio",
    "=": "Equal",
}


""" general expression """
ParserElement.set_default_whitespace_chars("\t")
# use after general colum parse


""" parse nested expression """
allowed_symbols = "=-+/,*. '"
thecontent = Word(alphanums + allowed_symbols)
parentheses = nested_expr("(", ")")  # , content=thecontent)
free_text = parentheses.suppress() + rest_of_line()


# nuclide format: 63-EU-151
nuclide = Combine(
    Word(nums)
    + Literal("-")
    + Word(alphas)
    + Literal("-")
    + Word(nums + alphas + allowed_symbols)
)


""" DATA - parse could cause error when DATA section has line break with no data"""
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
