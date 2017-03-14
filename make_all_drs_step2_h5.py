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
df = pd.read_sql("""
    SELECT *
    FROM RunInfo
    WHERE fDrsStep=0
        AND fROI=1024
    """, db)
for i in range(160):
    df["drs_T_{0:03d}".format(i)] = np.nan
df["duration"] = df.fRunStop - df.fRunStart
df["Time"] = df.fRunStart + df.duration/2
df.set_index("Time", inplace=True)

for n, night_group in tqdm(df.groupby("fNight")):
    path = "/fact/aux/{n}.FAD_CONTROL_TEMPERATURE.fits".format(n=n)

    try:
        t = Table.read(path)
        aux_file_time = pd.to_datetime(t["Time"]*24*3600*1e9, unit="ns")

        for row in night_group.itertuples():
            run_start = row.fRunStart - pd.Timedelta(seconds=30)
            run_stop = row.fRunStop + pd.Timedelta(seconds=30)
            mask = (aux_file_time > run_start) & (aux_file_time < run_stop)
            run_drs_temperatures = np.array(t[mask.values]["temp"])

            if len(run_drs_temperatures) > 1:
                run_aux_times_in_s = np.array(t[mask.values]["Time"])*24*3600
                for i, TT in enumerate(run_drs_temperatures.mean(axis=0)):
                    df.ix[row.name, "drs_T_{0:03d}".format(i)] = TT

    except FileNotFoundError as e:
        print(e)
        pass

df = df[~pd.isnull(df.drs_T_000)]
df.to_hdf("all_drs_step2.h5", "all_drs_step2")
