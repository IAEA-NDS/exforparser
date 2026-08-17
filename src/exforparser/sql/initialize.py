import pandas as pd
import json
import os
from sqlalchemy import text

from exforparser.config import (
    engines,
    ENTRY_DOI_PICKLE,
    REF_DOI_PICKLE,
    INSTITUTE_PICKLE,
    MASTER_GIT_REPO_PATH,
)
from .models_core import metadata

DOI_REF_PARSING_DIR = os.environ.get(
    "DOI_REF_PARSING_DIR",
    "/Users/okumuras/Dropbox/Development/doi_ref_parsing",
)
DOI_REF_ENTRY_DOI_PICKLE = os.path.join(
    DOI_REF_PARSING_DIR, "data/entries/entry_dois.pickle"
)
DOI_REF_METADATA_PICKLE = os.path.join(
    DOI_REF_PARSING_DIR, "data/references/ref_metadata.pickle"
)


def _first_existing_path(*paths):
    for path in paths:
        if path and os.path.exists(path):
            return path
    return paths[-1]


def update_entry_doi_from_reference_metadata(connection):
    result = connection.execute(
        text(
            """
            UPDATE entry_doi
            SET
                main_reference_doi = (
                    SELECT rm.doi
                    FROM reference_metadata rm
                    WHERE substr(entry_doi.exfor_main_reference, 2,
                                 length(entry_doi.exfor_main_reference) - 2) = rm.reference_code
                      AND rm.doi IS NOT NULL
                    LIMIT 1
                ),
                doi_source = CASE
                    WHEN entry_doi.exfor_main_reference LIKE '%JAEA%'
                      OR entry_doi.exfor_main_reference LIKE '%JAERI%'
                    THEN 'JaLC'
                    ELSE 'Crossref'
                END
            WHERE
                entry_doi.main_reference_doi IS NULL
                AND EXISTS (
                    SELECT 1
                    FROM reference_metadata rm
                    WHERE substr(entry_doi.exfor_main_reference, 2,
                                 length(entry_doi.exfor_main_reference) - 2) = rm.reference_code
                      AND rm.doi IS NOT NULL
                )
            """
        )
    )
    updated = result.rowcount if result.rowcount is not None else 0

    result = connection.execute(
        text(
            """
            INSERT INTO entry_doi (
                entry,
                exfor_main_reference,
                main_reference_doi,
                doi_source
            )
            SELECT
                eb.entry,
                eb.main_reference,
                eb.main_doi,
                eb.doi_source
            FROM exfor_bib eb
            WHERE eb.main_reference IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM entry_doi ed
                  WHERE ed.entry = eb.entry
              )
            """
        )
    )
    inserted = result.rowcount if result.rowcount is not None else 0
    return updated, inserted


def initialize_db():
    metadata.create_all(bind=engines["exfor"])
    # read_doi_pickles()


def load_pickles():

    entry_doi_pickle = _first_existing_path(DOI_REF_ENTRY_DOI_PICKLE, ENTRY_DOI_PICKLE)
    ref_metadata_pickle = _first_existing_path(DOI_REF_METADATA_PICKLE, REF_DOI_PICKLE)

    entry_doi_df = pd.read_pickle(entry_doi_pickle)
    ref_metadata_df = pd.read_pickle(ref_metadata_pickle)
    institute_df = pd.read_pickle(INSTITUTE_PICKLE)

    with engines["exfor"].begin() as connection:
        entry_doi_df = entry_doi_df.rename(columns={"exfor_entry": "entry"})
        entry_doi_df[
            ["entry", "exfor_main_reference", "main_reference_doi", "doi_source"]
        ].to_sql(
            "entry_doi",
            connection,
            index=False,
            if_exists="replace",
        )

        ref_metadata_df = ref_metadata_df.rename(
            columns={"article-number": "article_number"}
        )
        ref_metadata_df["authors"] = ref_metadata_df["authors"].apply(json.dumps)
        ref_metadata_df["first_author"] = ref_metadata_df["first_author"].astype(str)
        ref_metadata_df.to_sql(
            "reference_metadata",
            connection,
            index=False,
            if_exists="replace",
        )

        institute_df = institute_df.rename(columns={"code": "x4_code", "addres_country": "address_country"})
        institute_df.to_sql(
            "institute_geo_info",
            connection,
            index=False,
            if_exists="replace",
        )

        doi_updated, doi_inserted = update_entry_doi_from_reference_metadata(connection)

    print(f"Loaded entry_doi from {entry_doi_pickle}")
    print(f"Loaded reference_metadata from {ref_metadata_pickle}")
    print(f"Updated {doi_updated} entry_doi rows from reference_metadata")
    print(f"Inserted {doi_inserted} entry_doi rows from exfor_bib")

    return


def get_updated_entries():
    with open(
        os.path.join(MASTER_GIT_REPO_PATH, "entry_updatedate.dat")
    ) as ent_up_file:
        """
        read https://github.com/IAEA-NDS/exfor_master/blob/main/entry_updatedate.dat
        return df as follows
                    entry last_commit  num_updates last_update
            7072   22403  2023-09-28            5  2023-09-28
            7078   22409  2023-09-28            4  2023-09-28
        """
        ent_update_df = pd.read_table(
            ent_up_file,
            sep="\s+",
            header=None,
            names=["entry", "last_commit", "num_updates", "sha"],
        )
        ent_update_df["last_update"] = pd.to_datetime(
            ent_update_df["last_commit"].str[:10]
        )
        ent_update_df = ent_update_df.sort_values(by="last_update", ascending=False)

    return ent_update_df
