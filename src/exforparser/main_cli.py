import argparse
import os
import sqlalchemy as db
from sqlalchemy.exc import OperationalError

from exforparser.config import engines, OUT_PATH
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
    level_density,
    strength_function,
    transmission,
    angular_distribution,
    energy_distribution,
    double_differential_cross_section,
    fission_yield,
    neutron_observables,
    ion_crosssection,
)
from exforparser.tabulator.data_dir_files import write_list_files
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
        help="Parse EXFOR entries into JSON and SQL (SQLite). 'all', 'updated', and an entry number is allowed. Use -o ll to also write EXFORTABLES-format text files.",
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
            "thermal_reference",
            "xs",
            "ion",
            "energy",
            "ddx",
            "angle",
            "fy",
            "neutrons",
            "resonance_integral",
            "resonance_integral_pure_exfor",
            "resonance_parameter",
            "resonance_parameter_pure_exfor",
            "gamma_gamma",
            "gamma_gamma_pure_exfor",
            "macs",
            "macs_pure_exfor",
            "resonance_spacing",
            "resonance_spacing_pure_exfor",
            "level_density",
            "level_density_pure_exfor",
            "strength_function",
            "strength_function_pure_exfor",
            "transmission",
            "list",
        ],
        help='Write EXFORTABLES-format text files from SQLite Database. '
             '"ll": pure EXFOR observable types into exfortables_py (xs, angle, energy, ddx, fy, neutrons); '
             '"all": pure EXFOR plus legacy thermal/resonance outputs; '
             '"xs": cross sections; "ion": ion-induced cross sections; '
             '"angle": angular distributions; "energy": energy distributions; '
             '"ddx": double differential cross sections; '
             '"fy": fission yields; "neutrons": neutron observables; '
             '"thermal": pure EXFOR thermal cross sections; '
             '"thermal_reference": thermal cross sections in the reference output tree; '
             '"resonance_integral": resonance integrals; "macs": Maxwellian average cross sections; '
             '"gamma_gamma": average radiative widths; "resonance_spacing": level spacings; '
             '"resonance_parameter": resonance parameters; '
             '"level_density": level-density parameters; "strength_function": strength functions; '
             'append "_pure_exfor" to these resonance/scalar options to write only into exfortables_py; '
             '"transmission": transmission data; '
             '"list": scan output tree and write .list index files. '
             'Legacy options (all, level_density, strength_function) are kept for backwards compatibility.',
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
        process_all(write_files=False)

    elif args.tabulate == "updated":
        process_updated_entry(write_files=False)

    elif args.tabulate:
        process(args.tabulate, write_files=False)

    elif args.observables:
        logging.basicConfig(filename="observables.log", level=logging.DEBUG, filemode="w", force=True)

        try:
            connection = engines["exfor"].connect()
            metadata = db.MetaData()

        except OperationalError:
            print(
                "SQLite Database is missing. First run the --tabulate option to create SQLite Database."
            )
            exit()

        if args.observables == "all":
            crosssection()
            angular_distribution()
            energy_distribution()
            double_differential_cross_section()
            fission_yield()
            neutron_observables()
            resonance_integral(pure_exfor=True)
            macs(pure_exfor=True)
            gamma_gamma(pure_exfor=True)
            resonance_spacing(pure_exfor=True)
            resonance_parameter(pure_exfor=True)
            level_density(pure_exfor=True)
            strength_function(pure_exfor=True)
            transmission(pure_exfor=True)
            thermal("thermal")
            resonance_integral()
            macs()
            gamma_gamma()
            resonance_spacing()
            resonance_parameter()
            level_density()
            strength_function()
            # write_list_files()

        elif args.observables == "xs":
            crosssection()

        elif args.observables == "ion":
            ion_crosssection()

        elif args.observables == "thermal":
            thermal("thermal", pure_exfor=True)

        elif args.observables == "thermal_reference":
            thermal("thermal")

        elif args.observables == "resonance_integral":
            resonance_integral()

        elif args.observables == "macs":
            macs()

        elif args.observables == "gamma_gamma":
            gamma_gamma()

        elif args.observables == "resonance_spacing":
            resonance_spacing()

        elif args.observables == "resonance_parameter":
            resonance_parameter()

        elif args.observables == "level_density":
            level_density()

        elif args.observables == "strength_function":
            strength_function()

        elif args.observables == "transmission":
            transmission(pure_exfor=True)

        elif args.observables == "angle":
            angular_distribution()

        elif args.observables == "energy":
            energy_distribution()

        elif args.observables == "ddx":
            double_differential_cross_section()

        elif args.observables == "fy":
            fission_yield()

        elif args.observables == "neutrons":
            neutron_observables()

        elif args.observables == "list":
            write_list_files()

        # for backward compatibility
        # to write files in resonance_data[https://github.com/shinokumura/resonance_data] and thermaldata[github.com/shinokumura/thermaldata] repos.
        elif args.observables == "resonance_integral_pure_exfor":
            resonance_integral(pure_exfor=True)

        elif args.observables == "macs_pure_exfor":
            macs(pure_exfor=True)

        elif args.observables == "gamma_gamma_pure_exfor":
            gamma_gamma(pure_exfor=True)

        elif args.observables == "resonance_spacing_pure_exfor":
            resonance_spacing(pure_exfor=True)

        elif args.observables == "resonance_parameter_pure_exfor":
            resonance_parameter(pure_exfor=True)

        elif args.observables == "level_density_pure_exfor":
            level_density(pure_exfor=True)


        elif args.observables == "strength_function_pure_exfor":
            strength_function(pure_exfor=True)


if __name__ == "__main__":
    cli()
