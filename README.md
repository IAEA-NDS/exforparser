## Disclaimer
The repository is still under developments and not ready to use. It made
public to share the progress between collaborators. No documents are available yet.


## Using exforparser

### Load reaction index
There is prepared reaction index database in Python pickle format in ``pickles/reactions.pickle``. You can load and manipulate Pandas DataFrame for instance:

```
import pandas as pd
df = pd.read_pickle("pickles/reactions.pickle")

target = "79-AU-197"
process = "N,G"
quantity = "SIG"

df = df[
    (df_reaction.target == target.upper())
    & (df_reaction.process == process.upper())
    & (df_reaction.sf5.isnull())
    & (df_reaction.sf6 == quantity.upper())
    ]
print(df)
```

This pickle contains 499,023 records that looks like:

```
        id  entry subentry pointer  year       author  min_inc_en  max_inc_en points     target     process            sf4       residual   sf5      sf6   sf7    sf8   sf9
C0290009XX  C0290      009      XX  1981    R.A.Cecil   3.370e-04   3.370e-04      1   13-AL-27  10-NE-20,X         0-NN-1         0-NN-1  None    DA/DE  None   None  None
E1773008XX  E1773      008      XX  2002     T.Wakasa   3.450e+02   3.450e+02      1   20-CA-40         P,X         0-NN-1         0-NN-1  None    DA/DE  None   None  None
411280022   41128      002       2  1993 V.A.Anufriev         NaN         NaN      0  98-CF-250       N,TOT           None           None  None      WID  None   None  None
E2617012XX  E2617      012      XX  2019     T.Murata   3.270e+01   5.040e+01     15    39-Y-89         A,X        39-Y-87        39-Y-87  None      SIG  None   None  None
G0018003XX  G0018      003      XX  2010  Md.S.Rahman   5.000e+01   7.000e+01      3    49-IN-0         G,X  49-IN-111-G/M  49-IN-111-G/M  None  SIG/RAT  None    BRA  None
21909005XX  21909      005      XX  1979   H.Yamamoto   1.450e+01   1.450e+01      1   92-U-238         N,F           MASS          A=110   SEC       FY  None   None  None
E1434007XX  E1434      007      XX  1983  M.Takahashi   5.190e+01   5.190e+01      1  82-PB-208         P,T      82-PB-206      82-PB-206   PAR       DA  None   None  None
D6158002XX  D6158      002      XX  2008   R.Tripathi   7.000e+01   1.000e+02    169    39-Y-89    9-F-19,X           ELEM              C  None       DA  None   None  None
 120970097  12097      009       7  1960   H.B.Moller         NaN         NaN      0  64-GD-155       N,TOT           None           None  None      WID  None  SQ/S0  None
O0920008XX  O0920      008      XX  2001   J.Kuhnhenn   6.660e+01   6.660e+01      1    82-PB-0         P,F    47-AG-110-M    47-AG-110-M   IND      SIG  None   None  None
D0635002XX  D0635      002      XX  2003     W.Krolas   3.500e+02   3.500e+02      1  82-PB-208  28-NI-64,X      ELEM/MASS      47-Ag-110  None      SIG  None   None  None
D0635002XX  D0635      002      XX  2003     W.Krolas   3.500e+02   3.500e+02      1  82-PB-208  28-NI-64,X      ELEM/MASS      82-Pb-199  None      SIG  None   None  None
M06350212   M0635      021       2  2003 V.V.Varlamov   1.980e+01   2.760e+01     27    23-V-51        G,2N        23-V-49        23-V-49  None      SIG  None   None  EVAL
```

### Conversion of EXFOR to JSON
There are three ways to run the conversion. All converted JSON files are in [IAEA-NDS/exfor_json](https://github.com/IAEA-NDS/exfor_json) repository.

1. First, you need to download EXFOR master files from [IAEA-NDS/exfor_master](https://github.com/IAEA-NDS/exfor_master) repository.

2. Change the EXFOR master file path (``EXFOR_ALL_PATH``) and output path (``OUT_PATH``) in ``config.py``.

3. Convert from EXFOR to JSON, for instance, for EXFOR entry number 12898 and 40467:

```
import json
from exparser import convert_exfor_to_json
entries = ["12898", "40467"]
for entry in entries:
    entry_json = convert_exfor_to_json(entry)
    print(json.dumps(entry_json, indent = 1))

```

### Future works
More functions will come soon.

### Related works
[IAEA-NDS/exfor_master](https://github.com/IAEA-NDS/exfor_master)

[IAEA-NDS/exfor_json](https://github.com/IAEA-NDS/exfor_json)

[IAEA-NDS/exfor_dictionary](https://github.com/IAEA-NDS/exfor_dictionary)

