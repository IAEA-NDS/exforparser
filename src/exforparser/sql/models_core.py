import sqlalchemy as db
from sqlalchemy import MetaData, Table, Column
from sqlalchemy.dialects.sqlite import JSON

metadata = MetaData()

exfor_bib = Table(
    "exfor_bib",
    metadata,
    Column("entry", db.String, primary_key=True, unique=True),
    Column("title", db.String),
    Column("first_author", db.String),
    Column("authors", db.String),
    Column("first_author_institute", db.String),
    Column("main_facility_institute", db.String),
    Column("main_facility_type", db.String),
    Column("main_reference", db.String),
    Column("main_doi", db.String),
    Column("doi_source", db.String),
    Column("year", db.Integer),
)

exfor_histories = Table(
    "exfor_history",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry", db.String),
    Column("sha1", db.String),
    Column("latest_trans", db.String),
    # When this sha1 was first inserted into the DB
    Column("recorded_at", db.DateTime),
    # Actual git commit timestamp (populated by backfill; NULL for live-tracked records)
    Column("committed_at", db.DateTime),
    # True for the sha1 that is currently active in the master repo
    Column("is_current", db.Boolean),
    db.UniqueConstraint("entry", "sha1", name="uq_entry_sha1"),
)

exfor_experimental_condition = Table(
    "exfor_experimental_condition",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String),
    Column("x4_code", db.String),
    Column("type", db.String),
    Column("free_txt", db.String),
)

exfor_reactions = Table(
    "exfor_reactions",
    metadata,
    Column("entry_id", db.String, primary_key=True, unique=True),
    Column("entry", db.String),
    Column("target", db.String),
    Column("projectile", db.String),
    Column("process", db.String),
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
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String),
    Column("entry", db.String),
    Column("target", db.String),
    Column("projectile", db.String),
    Column("process", db.String),
    Column("sf4", db.String),
    Column("residual", db.String),
    Column("level_num", db.Integer),
    Column("e_out", db.Float),
    Column("en_inc_min", db.Float),
    Column("en_inc_max", db.Float),
    Column("points", db.Integer),
    Column("arbitrary_data", db.Boolean),
    Column("sf5", db.String),
    Column("sf6", db.String),
    Column("sf7", db.String),
    Column("sf8", db.String),
    Column("sf9", db.String),
    Column("x4_code", db.String),
    Column("mf", db.Integer),
    Column("mt", db.Integer),
    # x-axis (incident energy / kT) metadata
    Column("x_head", db.String),  # e.g. "EN", "KT", "EN-RES", "COS"
    Column("x_unit", db.String),              # base unit after conversion, e.g. "EV", "ADEG"
    # y-axis (observable) metadata
    Column("y_head", db.String),              # e.g. "DATA", "DATA-CM"
    Column("y_unit", db.String),              # base unit after conversion, e.g. "B", "B/SR"
)

exfor_data = Table(
    "exfor_data",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String),
    Column("en_inc", db.Float),
    Column("den_inc", db.Float),
    Column("en_inc_frame", db.String),  # "LAB", "CM", or NULL/unknown
    Column("charge", db.Float),
    Column("mass", db.Float),
    Column("isomer", db.String),
    Column("residual", db.String),
    Column("residual_type", db.String),
    Column("level_num", db.Integer),
    Column("data", db.Float),
    Column("ddata", db.Float),
    Column("data_frame", db.String),  # "LAB", "CM", or NULL/unknown
    Column("arbitrary_data", db.Boolean),
    Column("arbitrary_ddata", db.Boolean),
    Column("e_out", db.Float),
    Column("de_out", db.Float),
    Column("e_out_frame", db.String),  # "LAB", "CM", or NULL/unknown
    Column("angle", db.Float),
    Column("dangle", db.Float),
    Column("angle_frame", db.String),  # "LAB", "CM", or NULL/unknown
    Column("flags", db.String),
    Column("mf", db.Integer),
    Column("mt", db.Integer),
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
    Column("entry_id", db.String),   # FK-equivalent to exfor_indexes.entry_id
    Column("entry", db.String),
    Column("subent", db.String),
    Column("column_index", db.Integer),
    Column("column_type", db.String),            # "COMMON" or "DATA"
    Column("pointer", db.String),
    Column("head", db.String),        # original EXFOR column head, e.g. "KT", "EN"
    Column("unit", db.String),                    # original unit, e.g. "KEV", "MB"
    Column("data", db.String),                    # JSON list of raw values
)


exfor_references = Table(
    "exfor_references",
    metadata,
    Column("id", db.Integer, autoincrement=True, primary_key=True),
    Column("entry_id", db.String),
    Column("entry", db.String),
    Column("x4_code", db.String),
    Column("type", db.String),
    Column("free_txt", db.String),
    Column("year", db.Integer),
    Column("doi", db.String),
    Column("doi_source", db.String),
)

exfor_entry_dois = Table(
    "entry_doi",
    metadata,
    Column("entry", db.String, primary_key=True),
    Column("exfor_main_reference", db.String),
    Column("main_reference_doi", db.String),
    Column("doi_source", db.String),
)

exfor_reference_metadata = Table(
    "reference_metadata",
    metadata,
    Column("reference_code", db.String, primary_key=True),
    Column("doi", db.String),
    Column("volume", db.String),
    Column("page", db.String),
    Column("authors", JSON),
    Column("first_author", db.String),
    Column("title", db.String),
    Column("journal_title", db.String),
    Column("language", db.String),
    Column("issue", db.String),
    Column("publisher", db.String),
    Column("article_number", db.String),
)


exfor_institute_geo = Table(
    "institute_geo_info",
    metadata,
    Column("x4_code", db.String, primary_key=True),
    Column("name", db.String),
    Column("formatted_address", db.String),
    Column("address_country", db.String),
    Column("lat", db.String),
    Column("lng", db.String),
    Column("flag", db.String),
)
