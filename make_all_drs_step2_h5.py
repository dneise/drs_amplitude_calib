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
all_drs_step2 = pd.read_sql("select * from RunInfo where fDrsStep=2 and fNight>20150528 and fROI==300", db)
all_drs_step2["drs_temp_mean"] = np.nan
all_drs_step2["drs_temp_rms"] = np.nan


output = []

for n, g in tqdm(all_drs_step2.groupby("fNight")):
    n = str(n)
    y,m,d = n[0:4], n[4:6], n[6:8]
    path = "/fact/aux/{y}/{m}/{d}/{n}.FAD_CONTROL_TEMPERATURE.fits".format(y=y, m=m, d=d, n=n)
    try:
        t = Table.read(path)
        t["datetime"] = pd.to_datetime(t["Time"], unit="d")

        for row_id in tqdm(range(len(g))):
            row = g.iloc[row_id]
            r = row.fRunID
            start = row.fRunStart
            stop = row.fRunStop
            mask = (pd.Series(t["datetime"]) > start) & (pd.Series(t['datetime']) < stop)
            payload = np.array(t[mask.values]["temp"])
            if len(payload):
                row["drs_temp"] = payload.mean()
                row["drs_temp_rms"] = payload.std()

    
all_drs_step2["duration"] = all_drs_step2.fRunStop - all_drs_step2.fRunStart
all_drs_step2["Time"] = all_drs_step2.fRunStart + all_drs_step2.duration/2
all_drs_step2.set_index("Time", inplace=True)

all_drs_step2 = all_drs_step2[~pd.isnull(all_drs_step2.temp_mean)]
all_drs_step2 = all_drs_step2[all_drs_step2.fNight > 20150528]
all_drs_step2 = all_drs_step2[all_drs_step2.fROI == 300]

all_drs_step2.to_hdf("all_drs_step2.h5", "all_drs_step2")
