import sqlalchemy as db
from sqlalchemy import MetaData, Table, Column
from sqlalchemy.dialects.sqlite import JSON

metadata = MetaData()

exfor_bib = Table(
    "exfor_bib",
    metadata,
    Column("entry", db.String, primary_key=True, index=True, unique=True),
    Column("title", db.String, index=True),
    Column("first_author", db.String, index=True),
    Column("authors", db.String),
    Column("first_author_institute", db.String),
    Column("main_facility_institute", db.String, index=True),
    Column("main_facility_type", db.String, index=True),
    Column("main_reference", db.String),
    Column("main_doi", db.String),
    Column("doi_source", db.String),
    Column("year", db.Integer),
)

exfor_histories = Table(
    "exfor_history",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry", db.String, index=True),
    Column("sha1", db.String, index=True),
    Column("latest_trans", db.String, index=True),
    # When this sha1 was first inserted into the DB
    Column("recorded_at", db.DateTime, index=True),
    # Actual git commit timestamp (populated by backfill; NULL for live-tracked records)
    Column("committed_at", db.DateTime, index=True),
    # True for the sha1 that is currently active in the master repo
    Column("is_current", db.Boolean, index=True),
    db.UniqueConstraint("entry", "sha1", name="uq_entry_sha1"),
)

exfor_experimental_condition = Table(
    "exfor_experimental_condition",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String, index=True),
    Column("x4_code", db.String, index=True),
    Column("type", db.String),
    Column("free_txt", db.String),
)

exfor_reactions = Table(
    "exfor_reactions",
    metadata,
    Column("entry_id", db.String, primary_key=True, index=True, unique=True),
    Column("entry", db.String),
    Column("target", db.String, index=True),
    Column("projectile", db.String, index=True),
    Column("process", db.String, index=True),
    Column("sf4", db.String),
    Column("sf5", db.String),
    Column("sf6", db.String),
    Column("sf7", db.String),
    Column("sf8", db.String),
    Column("sf9", db.String),
    Column("x4_code", db.String),
    Column("math_expression", db.String),
)

exfor_indexes = Table(
    "exfor_indexes",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True, index=True),
    Column("entry_id", db.String, index=True),
    Column("entry", db.String),
    Column("target", db.String, index=True),
    Column("projectile", db.String, index=True),
    Column("process", db.String, index=True),
    Column("sf4", db.String),
    Column("residual", db.String, index=True),
    Column("level_num", db.Integer, index=True),
    Column("e_out", db.Float),
    Column("en_inc_min", db.Float, index=True),
    Column("en_inc_max", db.Float, index=True),
    Column("points", db.Integer, index=True),
    Column("arbitrary_data", db.Boolean, index=True),
    Column("sf5", db.String),
    Column("sf6", db.String, index=True),
    Column("sf7", db.String),
    Column("sf8", db.String),
    Column("sf9", db.String),
    Column("x4_code", db.String),
    Column("mf", db.Integer),
    Column("mt", db.Integer, index=True),
    # x-axis (incident energy / kT) metadata
    Column("x_head", db.String, index=True),  # e.g. "EN", "KT", "EN-RES", "COS"
    Column("x_unit", db.String),              # base unit after conversion, e.g. "EV", "ADEG"
    # y-axis (observable) metadata
    Column("y_head", db.String),              # e.g. "DATA", "DATA-CM"
    Column("y_unit", db.String),              # base unit after conversion, e.g. "B", "B/SR"
)

exfor_data = Table(
    "exfor_data",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String, index=True),
    Column("en_inc", db.Float),
    Column("den_inc", db.Float),
    # en_inc_frame (Boolean) removed — use exfor_indexes.x_head instead
    Column("charge", db.Float),
    Column("mass", db.Float),
    Column("isomer", db.String),
    Column("residual", db.String, index=True),
    Column("residual_type", db.String, index=True),
    Column("level_num", db.Integer, index=True),
    Column("data", db.Float),
    Column("ddata", db.Float),
    Column("arbitrary_data", db.Boolean),
    Column("arbitrary_ddata", db.Boolean),
    Column("e_out", db.Float),
    Column("de_out", db.Float),
    Column("e_out_frame", db.Boolean),
    Column("angle", db.Float, index=True),
    Column("dangle", db.Float),
    Column("flags", db.String),
    Column("mf", db.Integer),
    Column("mt", db.Integer, index=True),
    Column("en_inc_min", db.Float),
    Column("en_inc_max", db.Float),
    Column("e_out_min", db.Float),
    Column("e_out_max", db.Float),
)

# Stores the original EXFOR DATA/COMMON columns verbatim (heads, units, raw values).
# Acts as an audit log of the source data before unit conversion and tabulation.
exfor_native_data = Table(
    "exfor_native_data",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),  # was: entry as unique PK (bug)
    Column("entry_id", db.String, index=True),   # FK-equivalent to exfor_indexes.entry_id
    Column("entry", db.String, index=True),
    Column("subent", db.String, index=True),
    Column("column_index", db.Integer),
    Column("column_type", db.String),            # "COMMON" or "DATA"
    Column("pointer", db.String),
    Column("head", db.String, index=True),        # original EXFOR column head, e.g. "KT", "EN"
    Column("unit", db.String),                    # original unit, e.g. "KEV", "MB"
    Column("data", db.String),                    # JSON list of raw values
)


exfor_references = Table(
    "exfor_references",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String, index=True),
    Column("entry", db.String, index=True),
    Column("x4_code", db.String, index=True),
    Column("type", db.String),
    Column("free_txt", db.String),
    Column("year", db.Integer),
    Column("doi", db.String),
    Column("doi_source", db.String),
)

exfor_entry_dois = Table(
    "entry_doi",
    metadata,
    Column("entry", db.String, primary_key=True, index=True),
    Column("exfor_main_reference", db.String, index=True),
    Column("main_reference_doi", db.String),
    Column("doi_source", db.String),
)

exfor_reference_metadata = Table(
    "reference_metadata",
    metadata,
    Column("reference_code", db.String, primary_key=True, index=True),
    Column("doi", db.String, index=True),
    Column("volume", db.String),
    Column("page", db.String),
    Column("authors", JSON),
    Column("first_author", db.String, index=True),
    Column("title", db.String, index=True),
    Column("journal_title", db.String),
    Column("language", db.String),
    Column("issue", db.String),
    Column("publisher", db.String),
    Column("article_number", db.String),
)


exfor_institute_geo = Table(
    "institute_geo_info",
    metadata,
    Column("x4_code", db.String, primary_key=True, index=True),
    Column("name", db.String, index=True),
    Column("formatted_address", db.String),
    Column("address_country", db.String, index=True),
    Column("lat", db.String),
    Column("lng", db.String),
    Column("flag", db.String),
)
