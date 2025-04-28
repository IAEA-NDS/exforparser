import argparse

from .exforparser import convert, convert_all, convert_updated_entry
from .tabulate import process, process_all, process_updated_entry
from .tabulator.data_observables import crosssection, thermal, resonance_spacing, resonance_integral, gamma_gamma, macs
import logging


def cli():
    parser = argparse.ArgumentParser(prog="EXFOR Parser", add_help=False)

    parser.add_argument(
        "-c", 
        "--convert", 
        help="Convert EXFOR entry into JSON. 'all', 'updated', and an entry number is allowed."
    )
    parser.add_argument(
        "-t",
        "--tabulate",
        help="Convert EXFOR into tabulated tables in ASCII text. 'all', 'updated', and an entry number is allowed."
    ) 
    parser.add_argument(
        "-o",
        "--observables",
        choices=[
            "all",
            "thermal",
            "xs",
            "energy",
            "agnle",
            "fy",
            "resonance_integral",
            "resonance_parameters",
            "gamma_gamma",
            "macs",
            "resonance_spacing",
            "level_density",
            "strength_funcition"
        ],
        help='output EXFORTABLES like format from SQLite Database \n options: "all", "thermal": thermal cross section, "rp": resonance parameters, "ri": resonance integral, "xs": all cross sections, "energy": energy distributions, "agnle": anguler distributions, "fy": fission yields',
    )

    args = parser.parse_args()

    if args.convert:
        logging.basicConfig(filename="parsing.log", level=logging.DEBUG, filemode="w")

    if args.tabulate:
        logging.basicConfig(filename="tabulated.log", level=logging.DEBUG, filemode="w")

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

        import sqlalchemy as db
        from sqlalchemy.exc import OperationalError

        try:
            from .config import engine, session

            connection = engine.connect()
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



if __name__ == "__main__":
    cli()
