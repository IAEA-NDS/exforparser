import pandas as pd
import pickle

# try:
#     df_sig = pickle.load(open("reaction_sig.pickle", "rb"))
# except:
#     print("error")


def show_option():
    pd.reset_option("display.max_columns")
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1200)


# target = "40-zr-90"
target = "13-al-27"
process = "n,tot"
target = "92-u-235"
process = "n,f"
quantity = "SIG"
# show_option()
# try:
#     df_all = pickle.load(open("reactions.pickle", "rb"))
# except:
#     print("error")

# with pd.option_context("display.float_format", "{:11.3e}".format):
#     print(df_all)
#     df_all = df_all.sort_values(by=["year"])
#     # print(df_all[df_all["sf4"]=="ELEM/MASS"])
#     print(
#         df_all[(df_all.target == target.upper()) 
#             & (df_all.process == process.upper()) 
#             # & (df_all.sf4 is None)
#             & (df_all.sf5.isnull())
#             & (df_all.sf6 == quantity.upper())
#             ]
#     )




df1 = pickle.load(open("reactions_0527.pickle", "rb"))

entry = "12515"
target = "79-Au-197"
process = "N,G"
sf4 = "MASS"
quantity = "SIG"
sf8 = ["RES", "RTE", "SDT/AV", "SDT"]

show_option()
with pd.option_context("display.float_format", "{:11.3e}".format):
    df1 = df1[
    #     # (df1.entry == entry )
        (df1.target == target.upper())
        & (df1.process == process.upper()) 
        & (df1.sf5.isnull())
        & (df1.sf6 == quantity.upper())
        & (~df1.sf8.isin(sf8))
        & (df1.points > 0)
    #     # # & (df1.sf4 == sf4.upper())
                ]
    print(df1.sort_values(by=["year","entry","subentry"]))


# df_all = pd.read_pickle("reactions.pickle.cp")  
# df_all = pickle.load(open("reactions.pickle", "rb"))
# 