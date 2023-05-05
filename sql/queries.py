import pandas as pd
from collections import OrderedDict
from operator import getitem


from libraries2023.datahandle.list import elemtoz_nz
from sql.models import Exfor_Bib, Exfor_Reactions, Exfor_Data, Exfor_Indexes
from endflib_sql.models import Endf_Reactions, Endf_XS_Data, Endf_Residual_Data, Endf_FY_Data
from config import session, session_lib, engines
from common import energy_range_conversion


########  -------------------------------------- ##########
##         Join table for AGGrid
########  -------------------------------------- ##########
def join_reac_bib():
    connection = engines["exfor"].connect()
    all = session().query(Exfor_Indexes.entry_id, 
                          Exfor_Indexes.target,
                          Exfor_Indexes.process,
                          Exfor_Indexes.residual,
                          Exfor_Indexes.e_inc_min,
                          Exfor_Indexes.e_inc_max,
                          Exfor_Indexes.sf5,
                          Exfor_Indexes.sf6,
                          Exfor_Indexes.sf7,
                          Exfor_Indexes.sf8,
                          Exfor_Bib.authors,
                          Exfor_Bib.year,
                          Exfor_Bib.main_facility_institute,
                          Exfor_Bib.main_facility_type,
                          ).join(Exfor_Bib, Exfor_Bib.entry == Exfor_Indexes.entry
                                 ).order_by(Exfor_Bib.year.desc()) 
    df = pd.read_sql(
        sql=all.statement,
        con=connection,
    )
    # print(df.head())
    return df



def reaction_query_simple(type, elem, mass, reaction, branch):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
    connection = engines["exfor"].connect()
    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass

    if branch == "PAR":
        reac = session().query(Exfor_Reactions, Exfor_Bib).filter(
                Exfor_Reactions.target == target,
                Exfor_Reactions.process == reaction.upper(),
                Exfor_Reactions.sf5 == branch,
                Exfor_Reactions.sf6 == type.upper(),
            ).join(Exfor_Bib, Exfor_Reactions.entry == Exfor_Bib.entry, isouter=True)
        
    elif isinstance(branch, int):
        reac = session().query(Exfor_Reactions, Exfor_Bib).filter(
                Exfor_Reactions.target == target,
                Exfor_Reactions.process == reaction.upper(),
                Exfor_Reactions.level_num == branch,
                Exfor_Reactions.sf6 == type.upper(),
            ).join(Exfor_Bib, Exfor_Reactions.entry == Exfor_Bib.entry, isouter=True)
        
    else:
        reac = session().query(Exfor_Reactions, Exfor_Bib).filter(
                Exfor_Reactions.target == target,
                Exfor_Reactions.process == reaction.upper(),
                Exfor_Reactions.sf6 == type.upper(),
            ).join(Exfor_Bib, Exfor_Reactions.entry == Exfor_Bib.entry, isouter=True)


    df = pd.read_sql(
        sql=reac.statement,
        con=connection,
    )
    # print(df)
    return df



########  -------------------------------------- ##########
##         Reaction queries for the dataexplorer
########  -------------------------------------- ##########
def reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
    reac = None
    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass
    
    if type == "AGTEST":
        type = "SIG"

    if type == "SIG":
        if branch:
            if branch == "PAR":
                reac = session().query(Exfor_Indexes).filter(
                        Exfor_Indexes.target == target,
                        Exfor_Indexes.process == reaction.upper(),
                        Exfor_Indexes.sf5 == branch,
                        Exfor_Indexes.sf6 == type.upper(),
                    ).all()

            else:
                reac = session().query(Exfor_Indexes).filter(
                        Exfor_Indexes.target == target,
                        Exfor_Indexes.process == reaction.upper(),
                        Exfor_Indexes.level_num == branch,
                        Exfor_Indexes.sf6 == type.upper(),
                    ).all()

        else:
            reac = session().query(Exfor_Indexes).filter(
                    Exfor_Indexes.target == target,
                    Exfor_Indexes.process == reaction.upper(),
                    Exfor_Indexes.sf5 == None,
                    Exfor_Indexes.sf6 == type.upper(),
                ).all()
            
    elif type == "Residual":
        residual = rp_elem.capitalize() + "-" + str(rp_mass)

        reac = session().query(Exfor_Indexes).filter(
                Exfor_Indexes.target == target,
                Exfor_Indexes.projectile == reaction,
                Exfor_Indexes.residual == residual,
            ).all()
    

    entids = {}
    entries = []
    if reac:
        for ent in reac:
            entids[ent.entry_id] = {
                "e_inc_min": ent.e_inc_min,
                "e_inc_max": ent.e_inc_max,
                "points": ent.points,
                "sf5": ent.sf5,
                "sf8": ent.sf8,
                "x4_code": ent.x4_code,
            }
            entries += [ent.entry]

    return entids, entries



def get_entry_bib(entries):
    bib = session().query(Exfor_Bib).filter(Exfor_Bib.entry.in_(tuple(entries))).all()

    legend = {}

    for b in bib:
        legend[b.entry] = {
            "author": b.first_author,
            "year": b.year if b.year else "1900",
        }

    return OrderedDict(
        sorted(legend.items(), key=lambda x: getitem(x[1], "year"), reverse=True),
    )



def data_query(entids, branch=None):
    connection = engines["exfor"].connect()

    data = session().query(Exfor_Data).filter(
        Exfor_Data.entry_id.in_(tuple(entids)),
        Exfor_Data.level_num == branch)

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df



def lib_query(type, elem, mass, reaction, mt, rp_elem, rp_mass):

    target = elem + mass.zfill(3)
    if type == "SIG":
        type = "XS"

    if type == "AGTEST":
        type = "XS"

    if type=="Residual":
        residual = rp_elem.capitalize() + str(rp_mass)
        reac = session_lib().query(Endf_Reactions).filter(
                Endf_Reactions.target == target,
                Endf_Reactions.projectile == reaction.split(",")[0].lower(),
                Endf_Reactions.type == type.lower(),
                Endf_Reactions.residual == residual,
            ).all()
    
    else:
        reac = session_lib().query(Endf_Reactions).filter(
                Endf_Reactions.target == target,
                Endf_Reactions.projectile == reaction.split(",")[0].lower(),
                Endf_Reactions.process == reaction.split(",")[1].upper(),
                Endf_Reactions.type == type.lower(),
                Endf_Reactions.mt == mt if mt is not None else Endf_Reactions.mt is not None,
            ).all()

    libs = {}
    for r in reac:
        libs[r.reaction_id] = r.evaluation

    return libs



def lib_xs_data_query(ids):
    connection = engines["endftables"].connect()
    data = session().query(Endf_XS_Data).filter(Endf_XS_Data.reaction_id.in_(tuple(ids)))

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df



def lib_residual_data_query(ids):
    connection = engines["endftables"].connect()
    data = session().query(Endf_Residual_Data).filter(Endf_Residual_Data.reaction_id.in_(tuple(ids)))

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df





def fy_branch(branch):
    if branch == "PRE":
        return ["PRE", "TER", "QTR", "PRV", "TER/CHG"]

    if branch == "IND":
        return ["IND", "SEC", "MAS", "CHG", "SEC/CHN"]

    if branch == "CUM":
        return ["CUM", "CHN"]




def reaction_query_fy(type, elem, mass, reaction, branch, mesurement_opt_fy, energy_range):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5

    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass
    lower, upper = energy_range_conversion(energy_range)


    reac = session().query(Exfor_Indexes).filter(
            Exfor_Indexes.target == target,
            Exfor_Indexes.process == reaction.upper(),
            Exfor_Indexes.sf5.in_(tuple(fy_branch(branch))),
            Exfor_Indexes.sf6 == type.upper(),
            Exfor_Indexes.e_inc_min >= lower,
            Exfor_Indexes.e_inc_max <= upper,
            (Exfor_Indexes.sf4 == "MASS" if mesurement_opt_fy=="A" else Exfor_Indexes.sf4 == "ELEM" if mesurement_opt_fy=="Z" else Exfor_Indexes.sf4.isnot(None) ),
        ).all()

    entids = {}
    entries = []

    for ent in reac:
        entids[ent.entry_id] = {
            "e_inc_min": ent.e_inc_min,
            "e_inc_max": ent.e_inc_max,
            "points": ent.points,
            "sf8": ent.sf8,
        }
        entries += [ent.entry]

    return entids, entries




def lib_fy_data_query(ids):
    connection = engines["endftables"].connect()
    data = session().query(Endf_FY_Data).filter(Endf_FY_Data.reaction_id.in_(tuple(ids)))

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df



