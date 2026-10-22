# EXFOR Parser

`exforparser` parses the fixed-width EXFOR master files and produces three
related forms of data:

- one JSON document per EXFOR entry;
- a normalized SQLite database used for querying and tabulation;
- EXFORTABLES-style text files grouped by projectile, target, reaction, and
  observable.

The project is under active development. Output schemas and tabulation rules
may still change between releases.

## Requirements

- Python 3.11 or newer
- Git
- a local clone of [`exfor_master`](https://github.com/IAEA-NDS/exfor_master)

Dependencies, including `exfor_dictionary` and `doi-ref-parsing`, are installed
from `requirements.txt` by the Python package installer.

## Installation

```bash
git clone https://github.com/IAEA-NDS/exforparser.git
cd exforparser

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The editable install provides the `exforparser` command.

## Data directory

All runtime paths are derived from the `EXFORPARSER_DATA_DIR` environment
variable. If it is not set, the default is `~/Documents/nucleardata`.

The expected layout is:

```text
$EXFORPARSER_DATA_DIR/
├── EXFOR/
│   ├── exfor_master/
│   │   ├── entry_updatedate.dat
│   │   └── exforall/
│   ├── exfor_json/
│   │   └── json/
│   ├── exfortables_py/
│   └── exfortables.sqlite
└── endftables.sqlite          # optional; used by IAEA Nuclear Reaction Dataexplorer
```

For example:

```bash
export EXFORPARSER_DATA_DIR="$PWD/nucleardata"
mkdir -p "$EXFORPARSER_DATA_DIR/EXFOR"

git clone https://github.com/IAEA-NDS/exfor_master.git \
  "$EXFORPARSER_DATA_DIR/EXFOR/exfor_master"
git clone https://github.com/IAEA-NDS/exfor_json.git \
  "$EXFORPARSER_DATA_DIR/EXFOR/exfor_json"
git clone https://github.com/IAEA-NDS/exfortables_py.git \
  "$EXFORPARSER_DATA_DIR/EXFOR/exfortables_py"
```

The JSON and EXFORTABLES repositories are output trees. Keeping them as Git
clones makes it possible to inspect and publish the generated changes.

## Quick start

Initialize a new SQLite database, parse every EXFOR entry, and write JSON:

```bash
exforparser -i -t all
```

Then generate all pure-EXFOR tables under `EXFOR/exfortables_py`:

```bash
exforparser -o all
```

The two commands are intentionally separate: tabulation populates SQLite,
while observable export queries SQLite to create the text files.

For a complete rebuild, use a new empty SQLite database and clean output trees.
The GitHub Actions workflow does this automatically in an ephemeral runner.

## Command-line interface

### JSON conversion

```bash
exforparser -c 12898     # one entry
exforparser -c all       # every entry
exforparser -c updated   # entries changed in exfor_master
```

JSON files are written to:

```text
$EXFORPARSER_DATA_DIR/EXFOR/exfor_json/json/<first-three-characters>/<entry>.json
```

### SQLite tabulation

```bash
exforparser -i                   # create missing SQLite tables
exforparser -t 12898             # tabulate one entry and write its JSON
exforparser -t all               # tabulate all entries and write all JSON
exforparser -t updated           # process entries changed in exfor_master
```

`-t updated` compares the current `exfor_master` Git state with the persisted
entry index. Successfully processed entry IDs are passed directly to the
installed `doi_ref_parsing.process_updated_entries` API.

Additional database operations:

```bash
exforparser -l    # load DOI/reference/institute metadata from package data
exforparser -H    # backfill the full per-entry Git history into SQLite
```

`-H` requires the full history of `exfor_master`; a shallow clone is not
sufficient.

### EXFORTABLES output

The main aggregate modes are:

```bash
exforparser -o all       # pure EXFOR outputs in exfortables_py only
exforparser -o legacy    # legacy thermal and resonance output trees
```

`all` writes the following pure-EXFOR observables:

- cross sections, including ion-induced reactions;
- angular distributions;
- energy distributions;
- double-differential cross sections;
- fission yields;
- neutron observables;
- thermal data;
- resonance integrals, MACS, average radiative widths, and level spacings;
- resonance parameters, level density, strength functions, and transmission.

Pure EXFOR output is kept under `EXFOR/exfortables_py`. Legacy output is kept
outside that tree under `EXFOR/thermal` and `EXFOR/resonance_data`; some legacy
tables may combine EXFOR with reference/evaluated data.

Individual observable modes are also available:

```text
xs, ion, angle, energy, ddx, fy, neutrons, thermal, transmission,
resonance_integral, macs, gamma_gamma, resonance_spacing,
resonance_parameter, level_density, strength_function, list
```

For resonance/scalar observables, the historical unsuffixed modes write to the
legacy tree. Append `_pure_exfor` to write those individual observables under
`exfortables_py`, for example:

```bash
exforparser -o resonance_integral_pure_exfor
```

`thermal` already means pure EXFOR; use `thermal_reference` for its legacy
counterpart. `list` scans generated text files and creates `.list` indexes with
their data-row counts.

## DOI metadata integration

The [`doi-ref-parsing`](https://github.com/shinokumura/exfor_entry_doi)
dependency is installed as a Python package. No local repository path such as
`DOI_REF_PARSING_DIR` is required.

Incremental tabulation calls its Python API directly:

```text
exforparser -t updated
    -> doi_ref_parsing.process_updated_entries(updated_entry_ids)
```

The `-l` option loads the packaged entry DOI and reference metadata into the
SQLite database and supplements missing entry DOI records from parsed EXFOR
bibliography data.

## Automated generated-data updates

The `Update generated EXFOR repositories` GitHub Actions workflow checks out
`exfor_master`, `exfor_json`, and `exfortables_py` under the layout above. It
then:

1. installs the current parser checkout;
2. cleans the generated output trees;
3. runs `exforparser -i -t all`;
4. runs `exforparser -o all`;
5. validates the SQLite database and checks that JSON/table files exist;
6. optionally commits and pushes both generated-data repositories.

### Testing with forks

Run the workflow manually with:

```text
repository_owner: shinokumura
publish: false
```

This uses the following test forks and performs a build without pushing:

- [`shinokumura/exfor_master`](https://github.com/shinokumura/exfor_master)
- [`shinokumura/exfor_json`](https://github.com/shinokumura/exfor_json)
- [`shinokumura/exfortables_py`](https://github.com/shinokumura/exfortables_py)

To test publication, add a `DATA_REPOS_TOKEN` Actions secret with Contents
write access to `shinokumura/exfor_json` and
`shinokumura/exfortables_py`, then run with `publish: true`.

The `repository_owner` input is the single switch for all three repositories.
Select `IAEA-NDS` only when the production repositories and credentials are
ready.

### Scheduled execution

The workflow has a daily schedule at 15:00 UTC, but the scheduled job remains
disabled until this repository variable is set:

```text
EXFOR_SCHEDULE_ENABLED=true
```

Scheduled runs can be configured with:

```text
EXFOR_DATA_REPOSITORY_OWNER=shinokumura
EXFOR_PUBLISH_OUTPUTS=false
```

The safe defaults are the `shinokumura` forks and no publication. Workflow
concurrency prevents overlapping updates.

## Development

Run the test suite with:

```bash
pytest
```

The parser handles fixed-width, pointer-sensitive scientific data. Changes to
parsing, JSON, SQLite, or tabular output should include focused regression
tests using representative EXFOR records.

## Related repositories

- [`IAEA-NDS/exfor_master`](https://github.com/IAEA-NDS/exfor_master)
- [`IAEA-NDS/exfor_json`](https://github.com/IAEA-NDS/exfor_json)
- [`IAEA-NDS/exfortables_py`](https://github.com/IAEA-NDS/exfortables_py)
- [`IAEA-NDS/exfor_dictionary`](https://github.com/IAEA-NDS/exfor_dictionary)
- [`shinokumura/exfor_entry_doi`](https://github.com/shinokumura/exfor_entry_doi)

## License

The parser source code is distributed under the terms in [LICENSE](LICENSE).
