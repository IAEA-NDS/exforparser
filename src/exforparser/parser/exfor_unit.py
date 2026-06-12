import math

from exfor_dictionary.exfor_dict import Diction

d = Diction()

# Build additional_code → base-unit mapping once at import time.
# The base unit for each category is the entry whose unit_conversion_factor == 1.0.
_units_d = Diction("25").get_diction()
BASE_UNIT: dict[str, str] = {
    v["additional_code"]: u
    for u, v in _units_d.items()
    if v.get("unit_conversion_factor") == "1.0000E+00"
}


def get_base_unit(original_unit: str) -> str | None:
    """Return the base unit for *original_unit*, or None if unknown."""
    info = _units_d.get(original_unit, {})
    code = info.get("additional_code")
    return BASE_UNIT.get(code) if code else None


# Boltzmann constant in eV/K
_KB_EV_PER_K: float = 8.617333262e-5


def kt_to_ev(head: str, unit: str, data: list) -> tuple[list, str]:
    """Ensure KT-type column data is stored in eV.

    unify_units already converts KT/KEV → EV and KT/MEV → EV via the
    multiplicative factor table.  The only case it cannot handle is
    KT-K (head) / K (unit), where kT must be computed as kB × T:

        kT [eV] = T [K] × 8.617333e-5 eV/K

    For all other KT heads whose unit is already EV the data pass through
    unchanged.  Non-KT heads are also returned unchanged.
    """
    if not head.startswith("KT"):
        return data, unit
    if unit == "K":
        data = [v * _KB_EV_PER_K if v is not None else None for v in data]
        return data, "EV"
    # KEV/MEV/EV cases are already converted by unify_units; just return as-is
    return data, unit


def unify_units(data_dic):
    """
    Convert every column in *data_dic* to its SI-like base unit in-place and
    update the corresponding entry in data_dic["units"] to the base unit name.

    data_dic looks like:
        {'heads': ['KT', 'DATA', 'ERR-T'],
         'units': ['KEV', 'MB', 'MB'],
         'data':  [[25.0], [8.92], [0.28]]}

    After the call:
        'units': ['EV', 'B', 'B']
        'data':  [[25000.0], [8.92e-3], [2.8e-4]]
    """
    for i in range(len(data_dic["units"])):
        orig = data_dic["units"][i]
        head = data_dic["heads"][i]

        # COS-type heads (COS, COS-CM, COS-MIN, COS-MAX, …) hold dimensionless cosine
        # values regardless of the unit code; convert to degrees unconditionally.
        if "COS" in head:
            try:
                data_dic["data"][i] = [
                    math.degrees(math.acos(max(-1.0, min(1.0, n))))
                    if n is not None else None
                    for n in data_dic["data"][i]
                ]
                data_dic["units"][i] = "ADEG"
            except Exception:
                pass
            continue

        if orig in ("NO-DIM", "ARB-UNITS"):
            continue

        fac = d.get_unit_factor(orig)
        if fac is not None:
            data_dic["data"][i] = [
                n * float(fac) if n is not None else None
                for n in data_dic["data"][i]
            ]
            base = get_base_unit(orig)
            if base is not None:
                data_dic["units"][i] = base

    return data_dic
