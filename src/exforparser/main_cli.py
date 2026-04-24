import argparse
import sqlalchemy as db
from sqlalchemy.exc import OperationalError

from exforparser.config import engines
from exforparser.sql.initialize import initialize_db, load_pickles
from exforparser.json_converter import convert, convert_all, convert_updated_entry
from exforparser.tabulate import process, process_all, process_updated_entry
from exforparser.tabulator.data_observables import (
    crosssection,
    thermal,
    resonance_spacing,
    resonance_integral,
    gamma_gamma,
    macs,
    resonance_parameter,
)
import logging


def cli():
    parser = argparse.ArgumentParser(prog="EXFOR Parser", add_help=False)

    parser.add_argument(
        "-c",
        "--convert",
        help="Convert EXFOR entry into JSON. 'all', 'updated', and an entry number is allowed.",
    )

    parser.add_argument(
        "-i",
        "--init",
        help="Create and initialize the SQLite Database",
        action="store_true",
    )

    parser.add_argument(
        "-l", "--load", help="Load other data source from Pickles", action="store_true"
    )

    parser.add_argument(
        "-t",
        "--tabulate",
        help="Convert EXFOR into tabulated tables in ASCII text. 'all', 'updated', and an entry number is allowed.",
    )

    parser.add_argument(
        "-H",
        "--history",
        help="Backfill all historical git SHA1s for every EXFOR master file into the history DB. "
             "This is a one-time (or periodic maintenance) operation and can be slow to run through.",
        action="store_true",
    )

    parser.add_argument(
        "-o",
        "--observables",
        choices=[
            "all",
            "thermal",
            "xs",
            "energy",
            "angle",
            "fy",
            "resonance_integral",
            "resonance_parameter",
            "gamma_gamma",
            "macs",
            "resonance_spacing",
            "level_density",
            "strength_function",
        ],
        help='output EXFORTABLES like format from SQLite Database \n options: "all", "thermal": thermal cross section, "rp": resonance parameters, "ri": resonance integral, "xs": all cross sections, "energy": energy distributions, "angle": angular distributions, "fy": fission yields',
    )

    args = parser.parse_args()
    if args.init:
        initialize_db()

    if args.load:
        load_pickles()

    if args.history:
        from exforparser.parser.list_x4files import list_all_git_history
        from exforparser.sql.stored_insert import backfill_history_from_git
        print("Collecting full git history for all EXFOR master files (this may take several minutes)…")
        records = list_all_git_history()
        print(f"Found {len(records)} total commit records. Inserting into DB…")
        inserted, skipped = backfill_history_from_git(records)
        print(f"Done: {inserted} inserted, {skipped} already present.")

    if args.convert:
        logging.basicConfig(filename="parsing.log", level=logging.DEBUG, filemode="w", force=True)

    if args.tabulate:
        logging.basicConfig(filename="tabulated.log", level=logging.DEBUG, filemode="w", force=True)

    if args.convert == "all":
        convert_all()

    elif args.convert == "updated":
        convert_updated_entry()

    elif args.convert:
        convert(args.convert)

    elif args.tabulate == "all":
        process_all()

    elif args.tabulate == "updated":
        process_updated_entry()

    elif args.tabulate:
        process(args.tabulate)

    elif args.observables:
        try:
            connection = engines["exfor"].connect()
            metadata = db.MetaData()

        except OperationalError:
            print(
                "SQLite Database is missing. First run the --tabulate option to create SQLite Database."
            )
            exit()

        if args.observables == "xs":
            crosssection()

        if args.observables == "thermal":
            thermal("thermal")

        if args.observables == "resonance_integral":
            resonance_integral()

        if args.observables == "macs":
            macs()

        if args.observables == "gamma_gamma":
            gamma_gamma()

        if args.observables == "resonance_spacing":
            resonance_spacing()

        if args.observables == "resonance_parameter":
            resonance_parameter()


if __name__ == "__main__":
    cli()
