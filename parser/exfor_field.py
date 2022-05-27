from pyparsing import *
from .utilities import extract_key, combine_dict

capitals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
special_chars = "@#\":,.;+-*/'<> _^%$()&!?$*~="
nest = nestedExpr()

main_identifiers = ["TITLE", "REFERENCE", "AUTHOR", "INSTITUTE", "FACILITY"]

identifiers = [
    "ANALYSIS",
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
    "MISC-COL",
    "MONIT-REF",
    "MONITOR",
    "PART-DET",
    "RAD-DET",
    "REL-REF",
    "SAMPLE",
]

general_identifiers = [
    "ANALYSIS",
    "CORRECTION",
    "DETECTOR",
    "EN-SEC",
    "ERR-ANALYS",
    "FLAG",
    "INC-SOURCE",
    "INC-SPECT",
    "METHOD",
    "MISC-COL",
    "PART-DET",
    "RAD-DET",
    "SAMPLE",
]

referencelike_identifiers = ["REL-REF", "MONIT-REF"]

reactionlike_identifiers = ["ASSUMED", "MONITOR"]

decay_identitires = ["DECAY-DATA", "DECAY-MON", "LEVEL-PROP", "HALF-LIFE"]

# FLAG COMMENT HISTORY STATUS EXP-YEAR CRITIQUE MISC-COL ADD-RES MOM-SEC
# RESULT SAMPLE

ParserElement.set_default_whitespace_chars("\t")
# use after general colum parse
restofline = Word(alphanums + special_chars) + LineEnd().suppress()
general_next = White(" ", exact=11).suppress() + restofline
pointer = (White(" ", exact=1) | Word(nums + alphas, exact=1)).leave_whitespace()

""" Title """
title_fields = (
    ZeroOrMore(White(" ")).suppress() + restofline
)  # + ZeroOrMore(OneOrMore(White(" ")).suppress() + restOfLine)

""" Author """
quote = "'"
charinauthor = "'+-. \""
single_author = Word(alphas + charinauthor)
author_fields = (
    Literal("(").suppress()
    + single_author
    + ZeroOrMore(Literal(",").suppress() + single_author)
    + Literal(")").suppress()
)

""" Reference """
# 30283 (W,KROPFF MORENO,19740327), 24129 (B,PR.NUC.EN.,2,183,58), A0408001 (R,INDC(GER)-32/LN+SPECIAL,33,88)
charinreference = ",.-+/ #"
inparenthesref = Literal("(") + Word(alphanums + charinreference) + Literal(")")
reference_inside = Word(alphanums + charinreference) + ZeroOrMore(
    inparenthesref | Word(alphanums + charinreference)
)
reference_types = "034ABCJKPRSTWX,"  # defined in diction=4

reference_general = Combine(
    Literal("(") + Word(reference_types, exact=1) + reference_inside + Literal(")")
)
reference_combination = Combine(
    Literal("((")
    + Word(alphanums + charinreference)
    + ZeroOrMore(inparenthesref)
    + Word(alphanums + charinreference)
    + Literal("=")
    + Word(alphanums + charinreference)
    + ZeroOrMore(inparenthesref)
    + Word(alphanums + charinreference)
    + Literal("))")
)

refrences = ZeroOrMore(reference_general) | ZeroOrMore(reference_combination)
reference_next = White(" ", exact=11).suppress() + refrences  # + ZeroOrMore(restofline)
reference_fields = refrences + ZeroOrMore(reference_next)

""" Institute """
## may be able to improve by reading DICTION 3
institute = Word(alphanums + " ")
institute_code = (
    Literal("(").suppress()
    + institute
    + ZeroOrMore(Literal(",").suppress() + institute)
    + Literal(")").suppress()
)
institute_fields = institute_code + ZeroOrMore(
    White(" ", exact=11).suppress() + institute_code
)

""" Facility """
facility_code = (
    Literal("(").suppress()
    + Combine(
        ZeroOrMore(Word(capitals)("facil-code") + Literal(","))
        + institute("facil-insti")
    )
    + Literal(")").suppress()
)
facility_fields = facility_code + ZeroOrMore(
    White(" ", exact=11).suppress() + facility_code
)

""" Reaction """
# for the pointer fields
# flg field can be "MLGSCIAR...etc" so better to use alphanums, but better to evaluate number first
# flg             = (White(" ",exact=1).set_parse_action(replace_with("0")) | Word(nums+alphas,exact=1)).leave_whitespace()

charinreaction = "-+/,*"
inparenthes = Literal("(") + Word(alphanums + charinreaction) + Literal(")")
# nuclide format: 63-EU-151
nuclide = Combine(
    Word(nums)
    + Literal("-")
    + Word(alphas)
    + Literal("-")
    + Word(nums + alphas + charinreaction)
)

# inside of reaction string (without parenthes): 63-EU-151(A,N)65-TB-154-M2/M1,,SIG/RAT
reaction_str = Combine(
    nuclide("target")
    + Literal("(")
    + Word(alphanums + charinreaction)("react_process")
    + Literal(")")
    + ZeroOrMore(inparenthes | Word(charinreaction + alphanums)("observable"))
)

# parse EXFOR reaction code (not ratio)
single_reaction = Combine(Literal("(") + reaction_str + Literal(")"))

# or ratio
charinreactionratio = Literal("=/+-*")
reaction_ratio = Combine(
    Literal("(") + single_reaction + Literal("=/+-*") + single_reaction + Literal(")")
)


reaction_code = single_reaction | reaction_ratio

# catch free text after reaction code
reaction_text = reaction_code.suppress() + restOfLine + lineEnd().suppress()

# separate target - (reaction) - product and other  !!! not used
reaction_sep = (
    Literal("(").suppress()
    + nuclide
    + Combine(Literal("(") + Word(alphanums + charinreaction) + Literal(")"))
    + Combine(ZeroOrMore(nuclide) + ZeroOrMore(Word(charinreaction + alphanums)))
    + Literal(")").suppress()
)


nested_reactioncode = (
    Literal("((") + reaction_code + OneOrMore(Literal("/")) + Literal("))")
)

pointer_field = Group(pointer + restofline)
next_pt_field = (
    White(" ", exact=10).suppress() + pointer_field
)  # + Word(printables) OneOrMore(Word(printables) + LineEnd())
reaction_column = (
    Keyword("REACTION").suppress()
    + White(" ", exact=2).suppress()
    + pointer_field
    + ZeroOrMore(next_pt_field.leave_whitespace())
)

""" MONITOR keyword """
monitor = Combine(Literal("(") + Word("MONIT" + nums) + Literal(")"))

""" ASSUME keyword """
assumed = Word("ASSUM" + nums) + Literal(",").suppress()

""" 
DECAY-DATA, HALF-LIFE etc x4 codes like sentense in the parenthsis 

 D4030 DECAY-MON  (30-ZN-62,9.26HR,DG,548.4,0.152,
                         DG,596.7,0.257)
                  (30-ZN-63,38.1MIN,DG,669.8,0.084,
                         DG,962.2,0.066)
                  (30-ZN-65,244.1D,DG,1115.5,0.5075)
 C2200 DECAY-DATA (65-TB-151-G,17.609HR,DG,616.56,0.104,
                               DG,251.86,0.263,
                               DG,287.36,0.283,
                               DG,931.23,0.077)
"""
charinx4code = ".,+-/="
x4codelike = Combine(Literal("(") + Word(alphanums + charinx4code) + Literal(")"))
## catch free text after code
aftercode_text = x4codelike.suppress() + restOfLine + lineEnd().suppress()

### parse for decay like code
### white space appears in the code
#             ((189.)70-YB-169,32.026D, DG,198.0,0.358,
#                             DG,177.2,0.222)
decaycodelike = Combine(
    Literal("(")
    + Word(alphanums + charinx4code + " ")
    + (Literal(",") | Literal(")") | lineEnd().suppress())
)

decaycontinue = Combine(
    ZeroOrMore(White(" ")).suppress()
    + Word(alphanums + charinx4code)
    + (Literal(",") | Literal(")") | lineEnd().suppress())
)

afterdecay_text = (
    ZeroOrMore(decaycodelike | decaycontinue).suppress()
    + restOfLine
    + lineEnd().suppress()
)


## catch free text after code


""" with flag """
## for (1.)
flagged = Combine(Literal("(") + Word(nums + ".") + Literal(")"))
flaged_after_text = (
    (flagged | x4codelike).suppress() + restOfLine + lineEnd().suppress()
)
double_flaggedcode = Combine(
    Literal("(")
    + ZeroOrMore(flagged | monitor).suppress()
    + Word(alphanums + charinx4code)
    + ZeroOrMore(Word(",") + lineEnd()).suppress()
    + Literal(")")
)  # + ZeroOrMore(restOfLine)
doubleflaged_after_text = (
    double_flaggedcode.suppress() + restOfLine
)  # + ZeroOrMore(general_next)

"""
DECAY-DATA ((1.)84-PO-207,5.80HR,DG,2060.2,0.0132,
                            DG,1662.7,0.0032,
                            DG,1372.4,0.0122,
                            DG,249.6,0.0160)
"""
double_decaycode = Combine(
    Literal("(")
    + ZeroOrMore(flagged | monitor).suppress()
    + Word(alphanums + charinx4code + " ")
    + (Literal(",") | Literal(")") | lineEnd().suppress())
)


doubleflaged_decay_after_text = (
    double_decaycode.suppress() + restOfLine
)  # + ZeroOrMore(general_next)


"""
MONITOR, ASSUMED: reaction code like sentense in the parenthsis
e.g.
MONITOR    ((MONIT1)79-AU-197(N,2N)79-AU-196,,SIG)
MONITOR    (92-U-235(N,ABS),,ETA,,MXW) Value = 2.077 prt/reac
MONITOR    ((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))
ASSUMED    (ASSUM,77-IR-191(N,G)77-IR-192-G,,SIG)
"""


""" MONITOR """
charinmonitor = "=-+/,*."
# DECAY-MON  ((MONIT)11-NA-24,15.HR,DG,1370.,1.0)
# MONITOR    ((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))
monitor_str = Combine(
    ZeroOrMore(nuclide)
    + Word(alphanums + charinmonitor)
    + ZeroOrMore(inparenthes | Word(charinmonitor + alphanums))
)

double_monitorcode = Combine(
    Literal("(")
    + ZeroOrMore(monitor | assumed).suppress()
    + (reaction_str | monitor_str)
    + Literal(")")
)

double_monitorcode_after_text = double_monitorcode.suppress() + restOfLine


""" 
REL-REF and MONIT-REF : reference like code in the parenthsis

e.g.
1) double parentheses ((xxx) code )
30310.x4
MONIT-REF  ((MONIT1),Z.T.BOEDY,R,INDC(HUN)-10,197301)The same
MONIT-REF  ((MONIT)32619002,Lu Hanlin,J,CST,9,(2),113,197505)

2) Single parentheses ( code )
MONIT-REF  (20111002,H.Vonach+,J,ZP,237,155,1970)
           (,G.Winkler,W,WINKLER,1981) personal communication.

# 30501 MONIT-REF  ((MONIT2)31248007,S.K.Mangal+,J,NP,36,542,1962)
#                   (,Zhao Wenrong,R,INDC(CPR)-16,198908)
#                   (,,3,IRDF-2002,,2005)
"""
double_monitrefcode = (
    Literal("(").suppress()
    + ZeroOrMore(monitor).suppress()
    + ZeroOrMore(Word(alphanums)("ref-ent"))
    + Literal(",").suppress()
    + ZeroOrMore(Word(alphas + "-.+ ")("ref-author"))
    + Literal(",").suppress()
    + Combine(
        Word(alphanums + charinx4code)
        + ZeroOrMore(
            Literal("(")
            + Word(alphanums + charinx4code)
            + Literal(")")
            + Word(alphanums + charinx4code)
        )
    )("ref-ref")
    + Literal(")").suppress()
)

doublemonitor_after_text = double_monitrefcode.suppress() + restOfLine


"""
single rel ref
"""
relref_types = "ACDEIMNOR"  # from diction 17
relref = (
    Literal("(").suppress()
    + ZeroOrMore(Word(relref_types, exact=1)("relref-type") + Literal(",").suppress())
    + ZeroOrMore(Word(alphanums, min=5)("ref-ent"))
    + Literal(",").suppress()
    + Word(alphas + "-.+ ")("ref-author")
    + Literal(",").suppress()
    + Combine(
        Word(alphanums + charinx4code)
        + ZeroOrMore(
            Literal("(")
            + Word(alphanums + charinx4code)
            + Literal(")")
            + Word(alphanums + charinx4code)
        )
    )("ref-ref")
    + Literal(")").suppress()
)

relrefafter_text = relref.suppress() + restOfLine

# Literal(")") # + ZeroOrMore(restOfLine)
# Word(alphanums + charinreference) + ZeroOrMore(inparenthesref | Word(alphanums + charinreference))


# for ((2.)41-NB-98-M,51.MIN,DG) ISOMER.


""" DATA - parse could cause error when DATA section has line break wiyh
no data"""
head_str = Word(capitals + "q" + nums + "-+/\* ", exact=11) | Word(capitals + "q" + nums + "-+/\* ")
data_header = OneOrMore(head_str)

data_str = (
    White(" ", exact=11)
    | Word(" " + nums + "+-.eEdD", exact=11)
    | Word(" " + nums + "+-.eEdD")
)
data_body = data_str.leaveWhitespace() + ZeroOrMore(data_str.leaveWhitespace())



def decomp_section(identifier, s):
    """
    parse data for the case without pointer : Title, Ref, Author, Institute
    """
    spacelen = 11 - len(identifier)
    sec_str = (
        LineEnd().suppress()
        + Keyword(identifier).suppress()
        + White(" ", exact=spacelen).suppress()
        + restofline
        + ZeroOrMore(general_next)
    )
    # field_body  = sec_str.searchString(s)
    return sec_str.searchString(s)


def decomp_flagedsection(identifier, s):
    """
    parse data for the case with pointer :
    Institute (only one entry 20802 has pointer),
    MONITOR..etc
    """
    spacelen = 10 - len(identifier)
    if len(identifier) == 10:
        sec_str = (
            LineEnd().suppress()
            + Keyword(identifier).suppress()
            + pointer_field
            + ZeroOrMore(White(" ", exact=10).suppress() + pointer_field)
        )
    else:
        sec_str = (
            LineEnd().suppress()
            + (Keyword(identifier) + White(" ", exact=spacelen)).suppress()
            + pointer_field
            + ZeroOrMore(White(" ", exact=10).suppress() + pointer_field)
        )

    return sec_str.searchString(s)
