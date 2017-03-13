# coding: utf-8
import fact
from fact import credentials
import pandas as pd
import astropy
from astropy.io import fits
from astropy.table import Table
import numpy as np
from tqdm import tqdm

db = fact.credentials.create_factdb_engine()
df = pd.read_sql("select * from RunInfo where fDrsStep=0 and fNight>20150528 and fNight<20160825 and fROI=1024", db)
df["drs_temp_mean"] = np.nan
for i in range(160):
    df["drs_T_{0:03d}".format(i)] = np.nan
df["drs_temp_time"] = pd.tslib.Timedelta(0)
df["drs_temp_rms"] = np.nan
df["drs_temp_slope_K_per_s"] = np.nan
df["duration"] = df.fRunStop - df.fRunStart
df["Time"] = df.fRunStart + df.duration/2
df.set_index("Time", inplace=True)


mean, std = [], []

for n, g in tqdm(df.groupby("fNight")):
    path = "aux/{n}.FAD_CONTROL_TEMPERATURE.fits".format(n=n)

    try:
        t = Table.read(path)
        t["datetime"] = pd.to_datetime(t["Time"]*24*3600*1e9, unit="ns")

        for row_id in range(len(g)):
            row = g.iloc[row_id]
            r = row.fRunID
            start = row.fRunStart - pd.Timedelta(seconds=30)
            stop = row.fRunStop + pd.Timedelta(seconds=30)
            mask = (pd.Series(t["datetime"]) > start) & (pd.Series(t['datetime']) < stop)
            payload = np.array(t[mask.values]["temp"])

            if len(payload) > 1:
                ttt = np.array(t[mask.values]["Time"])*24*3600
                slope, _ = np.polyfit(ttt - ttt.mean(), payload.mean(axis=1), 1)
                df.ix[row.name, "drs_temp_time"] = stop - start
                df.ix[row.name, "drs_temp_mean"] = payload.mean()
                for i, TT in enumerate(payload.mean(axis=0)):
                    df.ix[row.name, "drs_T_{0:03d}".format(i)] = TT
                df.ix[row.name, "drs_temp_rms"] = payload.std()
                df.ix[row.name, "drs_temp_slope_K_per_s"] = slope


    except FileNotFoundError as e:
        print(e)
        pass

df = df[~pd.isnull(df.drs_temp_mean)]
df.to_hdf("all_drs_step2.h5", "all_drs_step2")
