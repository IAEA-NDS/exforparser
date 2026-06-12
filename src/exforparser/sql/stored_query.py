import json
import pandas as pd
import numpy as np
from sqlalchemy import select, distinct, or_, and_

from exforparser.submodules.utilities.reaction import resonance_parameter_sf6
from .models_core import (
    exfor_bib,
    exfor_indexes,
    exfor_data,
    exfor_histories,
)
from exforparser.config import engines
from .stored_insert import ensure_exfor_data_frame_columns


################################################################################
####        History / SHA versioning queries
################################################################################


def get_current_sha(entry: str) -> dict | None:
    """Return the currently active history record for an entry, or None."""
    stmt = (
        select(exfor_histories)
        .where(exfor_histories.c.entry == entry)
        .where(exfor_histories.c.is_current == True)
    )
    with engines["exfor"].connect() as conn:
        row = conn.execute(stmt).fetchone()
    return row._asdict() if row else None


def get_sha_history(entry: str) -> list[dict]:
    """Return all recorded SHA versions for an entry, newest first."""
    stmt = (
        select(exfor_histories)
        .where(exfor_histories.c.entry == entry)
        .order_by(exfor_histories.c.recorded_at.desc())
    )
    with engines["exfor"].connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return [r._asdict() for r in rows]


def get_all_current_shas() -> dict:
    """Return {entry: sha1} mapping for all currently active records."""
    stmt = select(exfor_histories.c.entry, exfor_histories.c.sha1).where(
        exfor_histories.c.is_current == True
    )
    with engines["exfor"].connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return {r.entry: r.sha1 for r in rows}


def get_entries_with_history() -> list[str]:
    """Return entries that have more than one recorded sha1 (i.e., were updated)."""
    from sqlalchemy import func
    stmt = (
        select(exfor_histories.c.entry)
        .group_by(exfor_histories.c.entry)
        .having(func.count(exfor_histories.c.id) > 1)
    )
    with engines["exfor"].connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return [r.entry for r in rows]


################################################################################
####        Observable specific search
################################################################################


def list_of_target(obs_type) -> list:
    if obs_type in ["xs", "thermal", "macs"]:
        condition = exfor_indexes.c.sf6 == "SIG"
    elif obs_type == "angular_distribution":
        condition = exfor_indexes.c.sf6 == "DA"
    elif obs_type == "energy_distribution":
        condition = exfor_indexes.c.sf6 == "DE"
    elif obs_type == "double_differential_cross_section":
        condition = exfor_indexes.c.sf6 == "DA/DE"
    elif obs_type == "neutrons":
        condition = exfor_indexes.c.sf6 == "NU"
    elif obs_type == "tty":
        condition = exfor_indexes.c.sf6 == "TTY"
    elif obs_type == "resonance_integral":
        condition = exfor_indexes.c.sf6 == "RI"
    elif obs_type == "resonance_parameter":
        condition = exfor_indexes.c.sf6.in_(resonance_parameter_sf6)
    elif obs_type == "gamma_gamma":
        condition = exfor_indexes.c.sf6.in_(["WID"])
    elif obs_type == "resonance_spacing":
        condition = exfor_indexes.c.sf6 == "D"
    elif obs_type == "level_density":
        condition = exfor_indexes.c.sf6.in_(["LDP"])
    elif obs_type == "strength_function":
        condition = exfor_indexes.c.sf6.in_(["STF"])
    elif obs_type == "transmission":
        condition = exfor_indexes.c.sf6 == "TRN"
    else:
        return []

    stmt = select(distinct(exfor_indexes.c.target)).where(condition)
    with engines["exfor"].connect() as conn:
        results = conn.execute(stmt).fetchall()

    return sorted(row[0] for row in results)


def list_of_reactions_and_entries(obs_type: str) -> dict:
    if obs_type in ["xs", "thermal", "macs"]:
        conditions = and_(
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.projectile.in_(["0", "N", "P", "D", "G", "T"]),
        )
    elif obs_type == "angular_distribution":
        conditions = exfor_indexes.c.sf6 == "DA"
    elif obs_type == "energy_distribution":
        conditions = exfor_indexes.c.sf6 == "DE"
    elif obs_type == "double_differential_cross_section":
        conditions = exfor_indexes.c.sf6 == "DA/DE"
    elif obs_type == "neutrons":
        conditions = exfor_indexes.c.sf6 == "NU"
    elif obs_type == "fission_yield":
        conditions = exfor_indexes.c.sf6 == "FY"
    elif obs_type == "level_density":
        conditions = exfor_indexes.c.sf6 == "LDP"
    elif obs_type == "strength_function":
        conditions = exfor_indexes.c.sf6 == "STF"
    elif obs_type == "tty":
        conditions = exfor_indexes.c.sf6 == "TTY"
    else:
        return {}

    stmt = (
        select(
            exfor_indexes.c.target, exfor_indexes.c.process, exfor_indexes.c.entry_id
        )
        .where(conditions)
        .distinct()
        .order_by(exfor_indexes.c.target)
    )

    with engines["exfor"].begin() as conn:
        results = conn.execute(stmt).fetchall()

    target_dict = {}
    for target, process, entry_id in results:
        target_dict.setdefault(target, {}).setdefault(process, []).append(entry_id)

    return target_dict


######### Data query ###########


def resonance_condition_data_query(target, reaction, entry_id, sf6):
    ent_subent = entry_id.rsplit("-", 1)[0]
    stmt_en = select(exfor_indexes.c.entry_id).where(
        exfor_indexes.c.entry_id.startswith(ent_subent),
        exfor_indexes.c.sf5.is_(None),
        exfor_indexes.c.sf6 == sf6,
        exfor_indexes.c.sf7.is_(None),
        exfor_indexes.c.projectile == reaction.split(",")[0].upper(),
        exfor_indexes.c.process.endswith("0"),
    )

    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt_en).fetchall()

    entries = [row.entry_id for row in result] if result else [None]
    try:
        assert len(entries) == 1
        return data_query_by_id("resonance_parameter", entries)
    except AssertionError as error:
        print(error)
        return data_query_by_id("resonance_parameter", [entries[0]])


def parse_flags(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except json.JSONDecodeError:
            return {}
    elif isinstance(x, dict):
        return x
    return {}


def resonance_parameter_data_query(obs_type, sf6, target, reaction):
    projectile = reaction.split(",")[0]
    resonance_data_reaction = [
        f"{projectile.upper()},{ejc}" for ejc in ["TOT", "G", "EL", "F", "A"]
    ]

    stmt_en = select(exfor_indexes.c.entry_id).where(
        and_(
            exfor_indexes.c.target == target,
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == sf6,
            exfor_indexes.c.sf7.is_(None),
            exfor_indexes.c.process.in_(resonance_data_reaction),
        )
    )

    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt_en).fetchall()
        width_ids = [row.entry_id for row in result]

    resonance_data_df = data_query_by_id(obs_type, width_ids)
    resonance_data_df["momentum_l"] = np.nan
    resonance_data_df["spin_j"] = np.nan
    resonance_data_df["en_res_type"] = None

    resonance_data_df["flags_dict"] = resonance_data_df["flags"].apply(parse_flags)
    resonance_data_df["has_momentum_l"] = resonance_data_df["flags_dict"].apply(
        lambda x: "MOMENTUM L" in x
    )
    resonance_data_df["has_spin_j"] = resonance_data_df["flags_dict"].apply(
        lambda x: "SPIN J" in x
    )

    for entry_id in resonance_data_df["entry_id"].unique():
        mask = resonance_data_df["entry_id"] == entry_id
        idxs = resonance_data_df[mask].index

        if (
            resonance_data_df[resonance_data_df["entry_id"] == entry_id]["en_inc"]
            .isnull()
            .values.all()
        ):
            en_df = resonance_condition_data_query(target, reaction, entry_id, "EN")
            if not en_df.empty:
                resonance_data_df.loc[idxs, "en_inc"] = en_df["data"].values
                resonance_data_df.loc[idxs, "den_inc"] = en_df["ddata"].values
                resonance_data_df["en_res_type"] = "EN"
        else:
            resonance_data_df["en_res_type"] = "EN-RES"

        if (
            resonance_data_df[resonance_data_df["entry_id"] == entry_id][
                "has_momentum_l"
            ]
            .eq(False)
            .all()
        ):
            momentum_df = resonance_condition_data_query(
                target, reaction, entry_id, "L"
            )
            if not momentum_df.empty:
                resonance_data_df.loc[idxs, "momentum_l"] = momentum_df["data"].values
        else:
            def extract_momentum_l(flags):
                try:
                    return flags.get("MOMENTUM L", {}).get("data", None)
                except Exception:
                    return None

            resonance_data_df.loc[mask, "momentum_l"] = resonance_data_df.loc[
                mask, "flags_dict"
            ].apply(extract_momentum_l)

        if (
            resonance_data_df[resonance_data_df["entry_id"] == entry_id]["has_spin_j"]
            .eq(False)
            .all()
        ):
            spin_df = resonance_condition_data_query(target, reaction, entry_id, "J")
            if not spin_df.empty:
                resonance_data_df.loc[idxs, "spin_j"] = spin_df["data"].values
        else:
            def extract_spin_j(flags):
                try:
                    return flags.get("SPIN J", {}).get("data", None)
                except Exception:
                    return None

            resonance_data_df.loc[mask, "spin_j"] = resonance_data_df.loc[
                mask, "flags_dict"
            ].apply(extract_spin_j)

    return resonance_data_df


def observable_data_query(obs_type, target, reaction):
    conditions = [
        exfor_indexes.c.target == target,
        exfor_indexes.c.arbitrary_data.is_(False),
        exfor_indexes.c.process == reaction,
    ]

    if obs_type == "xs":
        conditions += [
            exfor_indexes.c.projectile.in_(["0", "N", "P", "D", "G", "T"]),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
        ]
    elif obs_type == "thermal":
        conditions += [
            exfor_indexes.c.projectile == "N",
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
            exfor_indexes.c.en_inc_min >= 0.024,
            exfor_indexes.c.en_inc_max <= 0.026,
        ]
    elif obs_type == "macs":
        conditions += [
            exfor_indexes.c.projectile == "N",
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
            or_(
                exfor_indexes.c.x_head.like("KT%"),
                exfor_indexes.c.x_head.like("EN%")
            ),
            exfor_indexes.c.en_inc_min >= 23000,
            exfor_indexes.c.en_inc_max <= 35000,
        ]
    elif obs_type == "resonance_integral":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "RI",
            exfor_indexes.c.sf7.is_(None),
        ]
    elif obs_type == "resonance_parameter":
        return resonance_parameter_data_query(obs_type, target, reaction)
    elif obs_type == "gamma_gamma":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "WID",
            exfor_indexes.c.sf7.is_(None),
            exfor_indexes.c.sf8 == "AV",
        ]
    elif obs_type == "resonance_spacing":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "D",
            exfor_indexes.c.sf7.is_(None),
        ]
    elif obs_type == "level_density":
        conditions += [
            exfor_indexes.c.sf6 == "LDP",
        ]
    elif obs_type == "strength_function":
        conditions += [
            exfor_indexes.c.sf6 == "STF",
        ]

    stmt = select(exfor_indexes.c.entry_id).where(and_(*conditions))
    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt).fetchall()

    entries = [row.entry_id for row in result] if result else [None]
    return data_query_by_id(obs_type, entries)


def data_query_by_id(obs_type, entries):
    conditions = [exfor_data.c.entry_id.in_(entries)]

    if obs_type == "thermal":
        conditions += [
            exfor_data.c.en_inc >= 0.024,
            exfor_data.c.en_inc <= 0.026,
        ]
    elif obs_type == "macs":
        conditions += [
            exfor_data.c.en_inc >= 23000,
            exfor_data.c.en_inc <= 35000,
            # exfor_indexes.c.sf8.in_(["MXW", "SPA", "MXW/FCT"])
        ]

    index_metadata = (
        select(
            exfor_indexes.c.entry_id,
            exfor_indexes.c.entry,
            exfor_indexes.c.target,
            exfor_indexes.c.process,
            exfor_indexes.c.sf4,
            exfor_indexes.c.sf5,
            exfor_indexes.c.sf6,
            exfor_indexes.c.sf7,
            exfor_indexes.c.sf8,
            exfor_indexes.c.sf9,
            exfor_indexes.c.x4_code,
            exfor_indexes.c.x_head,
            exfor_indexes.c.x_unit,
            exfor_indexes.c.y_head,
            exfor_indexes.c.y_unit,
        )
        .where(exfor_indexes.c.entry_id.in_(entries))
        .distinct()
        .subquery()
    )

    stmt = (
        select(
            exfor_bib.c.first_author,
            exfor_bib.c.first_author_institute,
            exfor_bib.c.main_facility_institute,
            exfor_bib.c.main_facility_type,
            exfor_bib.c.main_reference,
            exfor_bib.c.year,
            index_metadata.c.entry_id,
            index_metadata.c.target,
            index_metadata.c.process,
            index_metadata.c.sf4,
            index_metadata.c.sf5,
            index_metadata.c.sf6,
            index_metadata.c.sf7,
            index_metadata.c.sf8,
            index_metadata.c.sf9,
            index_metadata.c.x4_code,
            exfor_data.c.residual,
            exfor_data.c.level_num,
            index_metadata.c.x_head,
            index_metadata.c.x_unit,
            index_metadata.c.y_head,
            index_metadata.c.y_unit,
            exfor_data.c.en_inc,
            exfor_data.c.den_inc,
            exfor_data.c.en_inc_frame,
            exfor_data.c.en_inc_min,
            exfor_data.c.en_inc_max,
            exfor_data.c.e_out,
            exfor_data.c.de_out,
            exfor_data.c.e_out_frame,
            exfor_data.c.angle,
            exfor_data.c.dangle,
            exfor_data.c.angle_frame,
            exfor_data.c.charge,
            exfor_data.c.mass,
            exfor_data.c.isomer,
            exfor_data.c.data,
            exfor_data.c.ddata,
            exfor_data.c.data_frame,
            exfor_data.c.arbitrary_data,
            exfor_data.c.flags,
            exfor_data.c.mf,
            exfor_data.c.mt,
        )
        .select_from(
            exfor_data.join(
                index_metadata,
                index_metadata.c.entry_id == exfor_data.c.entry_id,
                isouter=True,
            ).join(
                exfor_bib,
                index_metadata.c.entry == exfor_bib.c.entry,
            )
        )
        .where(and_(*conditions))
        .order_by(
            index_metadata.c.sf9,
            index_metadata.c.sf8,
            index_metadata.c.sf7,
            exfor_bib.c.year.asc(),
        )
    )

    with engines["exfor"].begin() as conn:
        ensure_exfor_data_frame_columns(conn)
        df = pd.read_sql(stmt, conn)

    return df
