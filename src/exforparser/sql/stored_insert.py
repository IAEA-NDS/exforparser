import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import insert, update, select

from .models_core import (
    exfor_bib,
    exfor_reactions,
    exfor_references,
    exfor_indexes,
    exfor_experimental_condition,
    exfor_data,
    exfor_native_data,
    exfor_histories,
)
from exforparser.config import engines


def insert_bib(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_bib)
        connection.execute(stmt, dictlist)


def insert_experimental_info(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_experimental_condition)
        connection.execute(stmt, dictlist)


def insert_native_data(datadict):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_native_data)
        connection.execute(stmt, datadict)


def insert_df_to_data(df):
    df2 = df.astype(object).where(pd.notnull(df), None)
    with engines["exfor"].begin() as connection:
        df2.to_sql(
            "exfor_data",
            connection,
            index=False,
            if_exists="append",
        )


def insert_reference(dictlist):
    if not dictlist:
        return
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_references)
        connection.execute(stmt, dictlist)


def insert_reaction(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_reactions)
        connection.execute(stmt, dictlist)


def insert_reaction_index(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_indexes)
        connection.execute(stmt, dictlist)


def upsert_entry_history(entry: str, sha1: str, latest_trans: str) -> None:
    """Update history for a single entry.

    - If the entry+sha1 pair is new: insert with is_current=True.
    - If the sha1 changed: mark old current record non-current, then insert or
      reactivate the new sha1.
    - If sha1 is unchanged: no-op.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with engines["exfor"].begin() as conn:
        current = conn.execute(
            select(exfor_histories.c.id, exfor_histories.c.sha1)
            .where(exfor_histories.c.entry == entry)
            .where(exfor_histories.c.is_current == True)
        ).fetchone()

        if current is None:
            conn.execute(
                insert(exfor_histories).values(
                    entry=entry, sha1=sha1, latest_trans=latest_trans,
                    recorded_at=now, is_current=True,
                )
            )
        elif current.sha1 != sha1:
            conn.execute(
                update(exfor_histories)
                .where(exfor_histories.c.id == current.id)
                .values(is_current=False)
            )
            existing = conn.execute(
                select(exfor_histories.c.id)
                .where(exfor_histories.c.entry == entry)
                .where(exfor_histories.c.sha1 == sha1)
            ).fetchone()
            if existing:
                conn.execute(
                    update(exfor_histories)
                    .where(exfor_histories.c.id == existing.id)
                    .values(is_current=True)
                )
            else:
                conn.execute(
                    insert(exfor_histories).values(
                        entry=entry, sha1=sha1, latest_trans=latest_trans,
                        recorded_at=now, is_current=True,
                    )
                )


def insert_history_bulk(df) -> None:
    """Sync the history table with the DataFrame produced by list_exfor_files().

    For each row (entry, sha1, latest_trans):
    - Entries not yet in DB: insert as current.
    - Entries whose sha1 changed: retire old record, insert/reactivate new sha1.
    - Entries with unchanged sha1: no-op.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with engines["exfor"].begin() as conn:
        rows = conn.execute(
            select(exfor_histories.c.entry, exfor_histories.c.id, exfor_histories.c.sha1)
            .where(exfor_histories.c.is_current == True)
        ).fetchall()
        current_db = {r.entry: (r.id, r.sha1) for r in rows}

        for _, row in df.iterrows():
            entry = row["entry"]
            sha1 = row["sha1"]
            latest_trans = row["latest_trans"]

            if entry not in current_db:
                conn.execute(
                    insert(exfor_histories).values(
                        entry=entry, sha1=sha1, latest_trans=latest_trans,
                        recorded_at=now, is_current=True,
                    )
                )
            elif current_db[entry][1] != sha1:
                conn.execute(
                    update(exfor_histories)
                    .where(exfor_histories.c.id == current_db[entry][0])
                    .values(is_current=False)
                )
                existing = conn.execute(
                    select(exfor_histories.c.id)
                    .where(exfor_histories.c.entry == entry)
                    .where(exfor_histories.c.sha1 == sha1)
                ).fetchone()
                if existing:
                    conn.execute(
                        update(exfor_histories)
                        .where(exfor_histories.c.id == existing.id)
                        .values(is_current=True)
                    )
                else:
                    conn.execute(
                        insert(exfor_histories).values(
                            entry=entry, sha1=sha1, latest_trans=latest_trans,
                            recorded_at=now, is_current=True,
                        )
                    )


def backfill_history_from_git(history_records: list[dict]) -> tuple[int, int]:
    """Insert historical git records produced by list_all_git_history().

    Each dict must have: entry, sha1, latest_trans, recorded_at, committed_at, is_current.

    Rules:
    - (entry, sha1) already in DB: skip, but patch committed_at when it was NULL.
    - is_current=True preserved only when no existing is_current=True row exists.

    Returns (inserted, skipped) counts.
    """
    inserted = 0
    skipped = 0

    with engines["exfor"].begin() as conn:
        existing_rows = conn.execute(
            select(
                exfor_histories.c.entry,
                exfor_histories.c.sha1,
                exfor_histories.c.committed_at,
            )
        ).fetchall()
        existing_set = {(r.entry, r.sha1) for r in existing_rows}
        # Track rows whose committed_at is still NULL so we can fill them in
        null_committed = {
            (r.entry, r.sha1) for r in existing_rows if r.committed_at is None
        }

        current_rows = conn.execute(
            select(exfor_histories.c.entry)
            .where(exfor_histories.c.is_current == True)
        ).fetchall()
        has_current = {r.entry for r in current_rows}

        for rec in history_records:
            key = (rec["entry"], rec["sha1"])
            if key in existing_set:
                # Backfill committed_at if it was missing on the existing row
                if key in null_committed and rec.get("committed_at"):
                    conn.execute(
                        update(exfor_histories)
                        .where(exfor_histories.c.entry == rec["entry"])
                        .where(exfor_histories.c.sha1 == rec["sha1"])
                        .values(committed_at=rec["committed_at"])
                    )
                    null_committed.discard(key)
                skipped += 1
                continue
            # Don't let backfill override an existing is_current=True from live tracking
            is_current = rec["is_current"] and rec["entry"] not in has_current
            conn.execute(
                insert(exfor_histories).values(
                    entry=rec["entry"],
                    sha1=rec["sha1"],
                    latest_trans=rec["latest_trans"],
                    recorded_at=rec.get("recorded_at"),
                    committed_at=rec["committed_at"],
                    is_current=is_current,
                )
            )
            existing_set.add(key)
            if is_current:
                has_current.add(rec["entry"])
            inserted += 1

    return inserted, skipped
