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
from pyparsing import *
from .exfor_field import *
from .utilities import flatten_list
from collections import defaultdict

def correct_pub_year(ref):

    year = ref.replace("(", "").replace(")", "").split(",")[-1]

    if len(year) == 2:
        return "19" + year

    elif len(year) == 4:
        if (year.startswith("20") or year.startswith("19")):
            ## 1960 or 2020
            return year

        elif not year.startswith("19"):
            ### 8811
            return "19" + year[0:2]

    elif len(year) == 6:
        if year.startswith("20"):
            ### 200109
            return year[0:4]
        elif year.startswith("19"):
            ###  196809
            return year[0:4]
        elif not year.startswith("19") and not year.startswith("20"):
            ###  680901, most of the case it could be 19s
            return "19" + year[0:2]

    elif len(year) == 8:
        ### 20001120
        return year[0:4]

    else:
        return year


def main_bib_dict(bib_section) -> dict:
    """
    return the bibliographic information only
    """
    s = "".join(bib_section)
    bib_dict = {}
    bib_dict = {
        "title": "",
        "references": [{"x4code": "", "publication year": ""}],
        "authors": [{"name": ""}],
        "institutes": [{"x4code": ""}],
    }

    for identifier in main_identifiers:
        field_body = decomp_section(identifier, s)
        reference = []

        if field_body:
            if identifier == "TITLE":
                title = " ".join(list(flatten_list(field_body))).title()
                bib_dict["title"] = title

            elif identifier == "REFERENCE":
                doi = [
                    s.replace("#doi:", "")
                    for s in list(flatten_list(field_body))
                    if "#doi:" in s
                ]
                # need to fix if the volume number is in parenthesis
                parsed = reference_fields.searchString(field_body[0])
                reference = list(flatten_list(parsed))
                bib_dict["references"] = [
                    {
                        "x4code": reference[i],
                        "publication year": correct_pub_year(reference[i]),
                    }
                    for i in range(len(reference))
                ]
                bib_dict["#doi"] = doi

            elif identifier == "AUTHOR":
                parsed = author_fields.searchString(field_body[0])
                authors = list(flatten_list(parsed))
                authors = [s for s in authors if s != "'"]
                authors = [s.replace("'", "").replace('"', "").strip() for s in authors]
                bib_dict["authors"] = [
                    {"name": authors[i].title()} for i in range(len(authors))
                ]

            elif identifier == "INSTITUTE":
                ## DICTION 3
                parsed = institute_fields.searchString(field_body[0])
                institutes = list(flatten_list(parsed))
                bib_dict["institutes"] = [
                    {"x4code": institutes[i]} for i in range(len(institutes))
                ]
                # str(i).zfill(3): institutes[i] for i in range(len(institutes))

            elif identifier == "FACILITY":
                ## DICTION 18
                parsed = facility_fields.searchString(field_body[0])
                facilities = list(flatten_list(parsed))
                ## return like this: ['REAC,1CANCRC', 'REAC,1USAMTR']
                bib_dict["facilities"] = []

                for f in facilities:
                    ff = f.split(",")

                    if len(ff) > 1:
                        bib_dict["facilities"].append(
                            {
                                "type": ff[0],
                                "x4code": ff[1],
                            }
                        )
                    else:
                        bib_dict["facilities"].append({"x4code": f})
            else:
                pass

    return bib_dict


def bib_extra_dict(bib_section) -> dict:
    s = "".join(bib_section)
    dict = {}
    identif_dict = {}

    for identifier in identifiers:
        field_body = decomp_flagedsection(identifier, s)

        if field_body and identifier:

            identif_dict = bib_measurement_condition_dict(identifier, field_body[0])
            dict[identifier] = identif_dict

    return dict


def bib_measurement_condition_dict(identifier, field_body) -> dict:
    """
    field_body looks like
    [[' ', '(1.) Thickness off 10.6 b/atom'], [' ', '(2.) Thickness off 28.8 b/atom'],
    """
    previous_pointer = ""
    after_text = []
    flag = ""
    x4code = ""
    decaying = False
    i = 0

    x4code_str = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for _, val in enumerate(field_body):
        pointer = val[0]

        if previous_pointer == "":
            previous_pointer = val[0]

        if val[1].startswith("((") and not "//" in val[1]:
            """
            catch double quated
            e.g. DECAY-DATA ((1.)55-CS-138-M,2.9MIN,DG) (6-)-STATE.
            """
            if pointer == " ":
                pointer = "XX"

            if identifier in general_identifiers:
                """val[1][1:] means omitting the first parenthesis"""
                try:
                    flag = flagged.parse_string(val[1][1:])[0]
                    i += 1
                except:
                    flag = i

                """ exclude flag and get coded inside parenthesis """
                try:
                    flag_code = double_flaggedcode.parse_string(val[1])
                except:
                    flag_code = None

                """ free text after the code () """
                after_text = doubleflaged_after_text.parse_string(val[1])

                """ set value into dict """
                x4code = flag_code

            elif identifier in reactionlike_identifiers:
                """
                MONITOR    ((MONIT1)79-AU-197(N,2N)79-AU-196,,SIG)
                MONITOR    ((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))
                MONITOR    ((79-AU-197(N,2N)79-AU-196,,SIG)//
                           (79-AU-197(N,2N)79-AU-196,,SIG))
                MONITOR    ((MONIT)13-AL-27(N,A)11-NA-24,,SIG)
                           Absolute measurements were made at En=4.5 and 5.0 MeV
                MONITOR    ((MONIT)29-CU-63(N,2N)29-CU-62,,SIG) 511+-15 mb
                            obtained by absolute beta counting in J,NP/A,93,218,
                """
                if identifier == "MONITOR":
                    ### parse ASSUMED or MONITOR from val[1][1:] <- skip first parenthesis
                    try:
                        flag = monitor.parse_string(val[1][1:])[0]
                        i += 1
                    except:
                        # flag = "NO-FL"
                        flag = i

                if identifier == "ASSUMED":
                    try:
                        flag = assumed.parse_string(val[1][1:])[0]
                        i += 1
                    except:
                        # flag = "NO-FL"
                        flag = i

                if not "/" in val[1]:
                    x4code = double_monitor.parse_string(val[1]).asList()
                    after_text = double_monitorcode_after_text.parse_string(val[1])

                else:
                    x4code = "cannot parse"
                    after_text = [""]

            elif identifier in referencelike_identifiers:
                """val[1][1:] means omitting the first parenthesis
                e.g.
                MONIT-REF  ((MONIT1),Z.T.BOEDY,R,INDC(HUN)-10,197301)The same
                MONIT-REF  ((MONIT)32619002,Lu Hanlin,J,CST,9,(2),113,197505)
                refer. for MONIT2 and MONIT3
                """
                try:
                    flag = monitor.parse_string(val[1][1:])[0]
                    i += 1
                except:
                    flag = i

                """ exclude flag and get coded inside parenthesis """
                try:
                    monit_ref_code = double_monitrefcode.parse_string(val[1]).asList()
                    # after_text = double_monitorcode_after_text.parse_string(val[1])
                    refent = monit_ref_code.get("ref-ent")
                    refauthor = monit_ref_code.get("ref-author")
                    refref = monit_ref_code.get("ref-ref")
                    x4code = {"ent": refent, "author": refauthor, "ref": refref}
                except:
                    x4code = None

                """ free text after the code () """
                after_text = doublemonitor_after_text.parse_string(val[1])

            elif identifier in decay_identitires:
                """
                LEVEL-PROP ((0.)12-MG-27,E-LVL=0.000,SPIN=0.5,PARITY=+1.)
                           ((1.)12-MG-27,E-LVL=0.987,SPIN=1.5,PARITY=+1.)
                DECAY-MON  ((MONIT)11-NA-24,15.HR,DG,1370.,1.0)
                DECAY-DATA ((1.)36-KR-85-M,4.48HR,DG,151.18,0.76)
                           ((2.)36-KR-87,76.3MIN,DG,402.6,0.492)
                DECAY-DATA ((1.)84-PO-207,5.80HR,DG,2060.2,0.0132,
                                            DG,1662.7,0.0032,
                                            DG,1372.4,0.0122,
                                            DG,249.6,0.0160)
                """
                # flag = "NO-FL"

                if identifier == "DECAY-MON":
                    try:
                        flag = monitor.parse_string(val[1][1:])[0]
                        i += 1
                    except:
                        flag = i
                else:
                    try:
                        flag = flagged.parse_string(val[1][1:])[0]
                        i += 1
                    except:
                        flag = i

                try:
                    x4code = double_decaycode.parse_string(val[1]).asList()
                except:
                    x4code = None

                if x4code and x4code[-1].endswith(","):
                    decaying = True

                if not decaying:
                    after_text = doubleflaged_decay_after_text.parse_string(val[1])

                else:
                    after_text = [""]

            """
            sotre data into python dictionary
            """
            try:
                x4code_str[pointer][str(flag)] = dict(
                    {
                        "x4code": x4code,
                        "freetext": [after_text[0]],
                    }
                )
            except:
                x4code_str[pointer][str(flag)] = dict(
                    {
                        "x4code": x4code,
                    }
                )

        elif (
            val[1].startswith("(")
            and not val[1].startswith("((")
            and not val[1].endswith("))")
        ):

            if pointer == " ":
                pointer = "XX"

            if identifier in general_identifiers:
                """
                for general parenthesis and flagged
                2cases exist:
                case1: (1.) for FLAG,
                case2: (53-I-130-G,12.36HR,DG) DECAY-DATA,
                        (SCIN) for DETECTOR,
                        (ACTIV) for METHOD,
                        (D-D) for INC-SOURCE ...etc
                INC-SOURCE (D-D) The average energy 1.35 and 1.80 MeV deuteron
                METHOD     (ACTIV)
                ERR-ANALYS (ERR-T) Total error:
                            * zero-thickness correction factor  1.0 +- 7%,
                            * zero-copper-backing correction factor  0.77 +- 2%.
                            * room-scattered neutron correction F.   0.87 +- 4%.
                           (ERR-S) Statistical error                    +- 5%,
                """
                try:
                    flag = flagged.parse_string(val[1])[0]
                except:
                    # flag = "NO-FL"
                    flag = i

                try:
                    x4code = x4codelike.parse_string(val[1])[0]
                    i += 1
                except:
                    x4code = None
                    flag = i

                try:
                    after_text = doubleflaged_after_text.parse_string(val[1])
                except:
                    after_text = [""]

            elif identifier in reactionlike_identifiers:
                """
                for reaction like like, e.g. MONITOR and ASSUMED
                MONITOR    (3-LI-6(N,T)2-HE-4,,SIG)
                ASSUMED    (ASSUM,77-IR-191(N,G)77-IR-192-G,,SIG)
                """
                try:
                    flag = flagged.parse_string(val[1])[0]
                except:
                    # flag = "NO-FL"
                    flag = i

                try:
                    x4code = double_monitorcode.parse_string(val[1]).asList()
                    i += 1
                except:
                    x4code = None
                    flag = i

                try:
                    after_text = double_monitorcode_after_text.parse_string(val[1])
                except:
                    after_text = [""]

            elif identifier in referencelike_identifiers:
                """
                for reference like, e.g. MONIT-REF, REL-REF
                eg.
                MONIT-REF  (11457001,J.P.Butler,J,CJP,41,372,196305)
                MONIT-REF  (A0169013,R.Weinreich+,J,ARI,31,223,1980)
                           (D4080004,F.Tarkanyi+,C,91JUELIC,,529,1991)
                REL-REF    (M,13729001,P.E.Koehler+,J,PR/C,54,1463,1996)
                REL-REF    (R,,H.Piel+,J,RCA,57,1,1992) The primary proton energy
                           was determined from the ratio of sigma(p,2n) and
                           sigma(p,n) on Cu-63 according to H. Piel et al.
                           Radiochimica Acta, 57,1,1992.
                REL-REF    (R,,C.Nordborg+,C,91JUELIC,,782,1991)  - JEF -file
                           (R,,S.F.Mughabghab+,B,NEUT.CS 1A,,1981) - resonance
                            parameters
                """
                # 以下、どちらか一つで良い
                try:
                    flag = flagged.parse_string(val[1])[0]
                except:
                    # flag = "NO-FL"
                    flag = i

                try:
                    code = relref.parse_string(val[1])
                    relreftype = code.get("relref-type")
                    relrefent = code.get("ref-ent")
                    relrefauthor = code.get("ref-author")
                    refref = code.get("ref-ref")

                    x4code = {
                        "type": relreftype,
                        "ent": relrefent,
                        "author": relrefauthor,
                        "ref": refref,
                    }
                    i += 1
                except:
                    x4code = None
                    flag = i

                try:
                    after_text = relrefafter_text.parse_string(val[1])
                except:
                    after_text = [""]

            elif identifier in decay_identitires or decaying:
                """
                DECAY-DATA (18-AR-41,103.5MIN,DG) HALF-LIFE MEASURED.
                DECAY-MON  (25-MN-54,303.D,DG,835.)
                DECAY-MON  (30-ZN-62,9.26HR,DG,548.4,0.152,
                                    DG,596.7,0.257)
                HALF-LIFE  (HL,30-ZN-71-M) VALUE TAKEN FROM CHART OF NUCLIDES.
                LEVEL-PROP (28-NI-62,E-LVL=0.,SPIN=0.0,PARITY=1.)
                """
                # flag = "NO-FL"
                flag = i

                try:
                    x4code = decaycodelike.parse_string(val[1]).asList()
                    i += 1
                except:
                    x4code = None

                if x4code[-1].endswith(","):
                    decaying = True

                if not decaying:
                    after_text = afterdecay_text.parse_string(val[1])

                else:
                    after_text = [""]

            elif identifier == "FACILITY":
                flag = i
                try:
                    parsed = facility_fields.searchString(field_body[0])
                    x4code = list(flatten_list(parsed))
                    # x4code = {"type": list(flatten_list(parsed))[0], "institute": list(flatten_list(parsed))[1]}
                    i += 1
                except:
                    x4code = None

                after_text = afterdecay_text.parse_string(val[1])

            """
            store data in to dictionary format
            """
            try:
                x4code_str[pointer][str(flag)] = dict(
                    {"x4code": x4code, "freetext": [after_text[0]]}
                )
            except:
                x4code_str[pointer][str(flag)] = dict(
                    {
                        "x4code": x4code,
                    }
                )

        elif val[1].startswith("((") or val[1].endswith("))"):
            """
            In case if ratio:
            MONITOR    ((79-AU-197(N,2N)79-AU-196,,SIG)//
                       (79-AU-197(N,2N)79-AU-196,,SIG))
            """
            if pointer == " ":
                pointer = "XX"
            if flag == "":
                # flag = "NO-FL"
                flag = i
            try:
                x4code_str[pointer][str(flag)]["x4code"].append("".join(val[1]))
            except:
                pass

        elif decaying:
            x4code += decaycontinue.parse_string(val[1]).asList()
            if x4code[-1].endswith(","):
                decaying = True
            else:
                decaying = False
            after_text = afterdecay_text.parse_string(val[1])

        else:
            ## free text only rows
            if pointer == " ":
                pointer = "XX"
            if flag == "":
                # flag = "NO-FL"
                flag = i

            x4code_str[pointer][str(flag)]["freetext"].append("".join(val[1]))

        if pointer != " ":
            previous_pointer = pointer

    # print (json.dumps(x4code_str)), indent=1))
    # return json.loads(json_util.dumps(x4code_str))

    return dict(x4code_str)


# https://www.analyticsvidhya.com/blog/2020/08/query-a-mongodb-database-using-pymongo/TypeError: Object of type ObjectId is not JSON serializable
# https://www.mongodb.com/docs/manual/tutorial/model-referenced-one-to-many-relationships-between-documents/
