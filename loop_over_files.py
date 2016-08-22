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
all_drs_step2 = pd.read_sql("select * from RunInfo where fDrsStep=2 and fNight>20140000", db)

output = []

for g in tqdm(all_drs_step2.groupby("fNight")):
  n, g = g
  y,m,d = str(n)[0:4], str(n)[4:6], str(n)[6:8]
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
            output.append({"fNight":n, "fRunID":r, "temp_mean":payload.mean(), "temp_min":payload.min(), "temp_max":payload.max()})
          else:
            output.append({"fNight":n, "fRunID":r, "temp_mean":np.nan, "temp_min":np.nan, "temp_max":np.nan})
  except FileNotFoundError:
    for row_id in tqdm(range(len(g))):
        row = g.iloc[row_id]
        r = row.fRunID
        output.append({"fNight":n, "fRunID":r, "temp_mean":np.nan, "temp_min":np.nan, "temp_max":np.nan})


dd = pd.DataFrame(output)
dd.to_hdf("drs_temp.h5", "temps")
    
