# Define the Gaussian function
import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colormaps

def gaussian(x_range, amp, mu, sig):
    if amp == 0:
    # amp = 1/( (2 * math.pi) ** (1/2) * sig)
        amp = 1/(np.sqrt(2*math.pi) * sig)
    return amp * np.exp(-np.power(x_range - mu, 2.0) / (2 * np.power(sig, 2.0)))


def data_read():
    iq_data = pd.read_csv("/Users/okumuras/Dropbox/2025/Private/IQcount.txt", skiprows=1, sep='\t', header=None, names=["IQ", "Day_1","Day_2","Day_3","Day_4"])
    iq_data["Day_1"] = iq_data['Day_1'].replace(0, np.nan)
    iq_data["Day_2"] = iq_data['Day_2'].replace(0, np.nan)
    iq_data["Day_3"] = iq_data['Day_3'].replace(0, np.nan)
    iq_data["Day_4"] = iq_data['Day_4'].replace(0, np.nan)
    print(iq_data)
    return iq_data


def Gauss(x, A, B):
    y = A*np.exp(-1*B*x**2)
    return y

iq_data = data_read()
barshift = 0
colorshift = 0.25
plt.rcParams["font.size"] = 12

cmap = plt.get_cmap("Blues")
plt.set_cmap('ocean')
for column in iq_data.loc[:, iq_data.columns != 'IQ']:
    df = iq_data.dropna(subset=[column]) 
    popt, pcov = curve_fit(
                        gaussian,
                        df["IQ"].to_list(), 
                        df[column].to_list(),
                        p0 = [df[column].max(), 100, 10],
                        maxfev=1000,
                        absolute_sigma=True,)

    plt.plot(df["IQ"], gaussian(df["IQ"], *popt), '-', label=f"{column} fit, Median: {popt[1]:#.1f}", color=cmap(colorshift))
    plt.bar( df["IQ"] + barshift, df[column], label=column, edgecolor='white', width=0.5, alpha=0.7, color=cmap(colorshift))
    barshift += 0.1
    colorshift += 0.25


plt.xticks(np.arange(86,130,2))
plt.xlabel('Ski IQ')
plt.ylabel('Number of runs')
plt.legend()
# plt.grid()
plt.show()