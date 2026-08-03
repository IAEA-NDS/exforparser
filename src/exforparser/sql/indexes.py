"""Index definitions for the EXFOR database."""

from sqlalchemy import text
from sqlalchemy.engine import Engine


# Explicit indexes present in the current EXFOR database. SQLite indexes created
# automatically for primary-key and unique constraints are intentionally omitted.
INDEX_EXFOR_DB = (
    "CREATE INDEX IF NOT EXISTS ix_entry_doi_entry ON entry_doi (entry)",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_exfor_bib_entry ON exfor_bib (entry)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_bib_first_author ON exfor_bib (first_author)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_bib_main_facility_institute "
    "ON exfor_bib (main_facility_institute)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_bib_main_facility_type "
    "ON exfor_bib (main_facility_type)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_bib_title ON exfor_bib (title)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_bib_year ON exfor_bib (year)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_angle ON exfor_data (angle)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_en_inc ON exfor_data (en_inc)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_entry_id ON exfor_data (entry_id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_level_num ON exfor_data (level_num)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_mt ON exfor_data (mt)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_residual ON exfor_data (residual)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_data_residual_type "
    "ON exfor_data (residual_type)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_experimental_condition_entry_id "
    "ON exfor_experimental_condition (entry_id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_experimental_condition_x4_code "
    "ON exfor_experimental_condition (x4_code)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_histories_entry_cur "
    "ON exfor_history (entry, is_current)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_history_committed_at "
    "ON exfor_history (committed_at)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_history_entry ON exfor_history (entry)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_history_is_current "
    "ON exfor_history (is_current)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_history_latest_trans "
    "ON exfor_history (latest_trans)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_history_recorded_at "
    "ON exfor_history (recorded_at)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_history_sha1 ON exfor_history (sha1)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_arbitrary_data "
    "ON exfor_indexes (arbitrary_data)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_en_inc_max "
    "ON exfor_indexes (en_inc_max)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_en_inc_min "
    "ON exfor_indexes (en_inc_min)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_entry ON exfor_indexes (entry)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_entry_id "
    "ON exfor_indexes (entry_id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_id ON exfor_indexes (id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_level_num "
    "ON exfor_indexes (level_num)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_mt ON exfor_indexes (mt)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_points ON exfor_indexes (points)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_process "
    "ON exfor_indexes (process)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_projectile "
    "ON exfor_indexes (projectile)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_residual "
    "ON exfor_indexes (residual)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_sf6 ON exfor_indexes (sf6)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_target ON exfor_indexes (target)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_tgt_proj_sf56 "
    "ON exfor_indexes (target, projectile, sf5, sf6)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_tgt_proj_sf6 "
    "ON exfor_indexes (target, projectile, sf6)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_indexes_x_head ON exfor_indexes (x_head)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_native_data_entry "
    "ON exfor_native_data (entry)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_native_data_entry_id "
    "ON exfor_native_data (entry_id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_native_data_head ON exfor_native_data (head)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_native_data_subent "
    "ON exfor_native_data (subent)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_reactions_entry "
    "ON exfor_reactions (entry)",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_exfor_reactions_entry_id "
    "ON exfor_reactions (entry_id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_reactions_process "
    "ON exfor_reactions (process)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_reactions_projectile "
    "ON exfor_reactions (projectile)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_reactions_target "
    "ON exfor_reactions (target)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_references_entry "
    "ON exfor_references (entry)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_references_entry_id "
    "ON exfor_references (entry_id)",
    "CREATE INDEX IF NOT EXISTS ix_exfor_references_x4_code "
    "ON exfor_references (x4_code)",
)


def create_db_indexes(engine: Engine) -> None:
    """Create the EXFOR database indexes transactionally and idempotently."""
    with engine.begin() as conn:
        for ddl in INDEX_EXFOR_DB:
            conn.execute(text(ddl))
