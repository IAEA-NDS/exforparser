import os
from config import OUT_PATH
from tabulated.exfor_reaction_mt import mt_fy, rp_sig, mt_to_reaction

mt_dict, sf3_dict = mt_to_reaction()

def get_dir_name(react_dict, mt):
    ### generate output dir and filename
    return os.path.join(
        OUT_PATH,
        "exfortables",
        react_dict["process"].split(",")[0] if "-" not in react_dict["process"].split(",")[0] else "I/" + react_dict["process"].split(",")[0],
        react_dict["target"],
        # react_dict["target"].split("-")[1].capitalize()
        # + react_dict["target"].split("-")[2],
        react_dict["sf6"],
        # react_dict["process"].replace(",", "-"),
        mt,
    )


# def get_dir_name_par_sig(react_dict, mt):
#     ### generate output dir and filename
#     return os.path.join(
#         OUT_PATH,
#         "exfortables",
#         react_dict["process"].split(",")[0] if "-" not in react_dict["process"].split(",")[0] else ["I", react_dict["process"].split(",")[0]],
#         react_dict["target"],
#         # react_dict["target"].split("-")[1].capitalize()
#         # + react_dict["target"].split("-")[2],
#         react_dict["sf6"],
#         # react_dict["process"].replace(",", "-"),
#         mt,
#     )


def exfortables_filename_sig(dir, id, mt, prod, react_dict, bib):

    return os.path.join(
        dir,
        (
            react_dict["process"].replace(",", "-").lower()
            + "_"
            + react_dict["target"].split("-")[1].capitalize()
            + react_dict["target"].split("-")[2]
            + "_"
            + "MT"
            + str(mt)
            + "_"
            + str(prod)
            + "_"
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "_"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )



def exfortables_filename_da(dir, id, mt, en, prod, react_dict, bib):

    return os.path.join(
        dir,
        (
            react_dict["process"].replace(",", "-").lower()
            + "_"
            + react_dict["target"].split("-")[1].capitalize()
            + react_dict["target"].split("-")[2]
            + "_"
            + "MT"
            + str(mt)
            + "_"
            + "E"
            + ("{:.3e}".format(en) if en < 1.0 else "{:08.3f}".format(en))
            + "_"
            + str(prod)
            + "_"
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "_"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )




def exfortables_filename_fy(dir, id, mt, en, react_dict, bib):

    return os.path.join(
        dir,
        (
            react_dict["process"].replace(",", "-").lower()
            + "_"
            + react_dict["target"].split("-")[1].capitalize()
            + react_dict["target"].split("-")[2]
            + "_"
            + "MT"
            + mt
            + "_"
            + "E"
            + ("{:.3e}".format(en) if en < 1.0 else "{:08.3f}".format(en))
            + "_"
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "_"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )
