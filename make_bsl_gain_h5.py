# coding: utf-8
import pandas as pd
import os
from astropy.io import fits
from tqdm import tqdm, trange
import numpy as np
from sklearn import linear_model, datasets
import h5py

x = pd.HDFStore("h5/all_drs_step2.h5")["all"]
x = x.sort_values("temp_mean")

if os.path.isfile("h5/bsl_gain.h5"):
    os.unlink("bsl_gain.h5")

h = h5py.File("h5/bsl_gain.h5")
chunk_N = 32
bsl = h.create_dataset("bsl", shape=(len(x), 1440, 1024), dtype=np.float32, fillvalue=np.nan, chunks=(chunk_N, 1440, 32))
gain = h.create_dataset("gain", shape=(len(x), 1440, 1024), dtype=np.float32, fillvalue=np.nan, chunks=(chunk_N, 1440, 32))

for chunk_id in trange(len(x)//chunk_N +1):
    b_chunk = np.ones((chunk_N, 1440, 1024), dtype=np.float32) * np.nan
    g_chunk = np.ones((chunk_N, 1440, 1024), dtype=np.float32) * np.nan

    for i in range(chunk_N):
        run_id = chunk_id * chunk_N + i
        try:
            run = x.iloc[run_id]
        except IndexError:
            break

        path = "./data/{n}_{r:03d}.drs.fits.gz".format(n=run.fNight, r=run.fRunID)

        try:
            with fits.open(path) as f:
                b = f[1].data["BaselineMean"].reshape(1440, -1).astype('f4')
                g = f[1].data["GainMean"].reshape(1440, -1).astype('f4')
                b_chunk[i, ...] = b[...]
                g_chunk[i, ...] = g[...]
        except FileNotFoundError:
            print(path, "not found")
            pass

    s = slice(chunk_id*chunk_N, (chunk_id+1) * chunk_N)
    bsl[s,...] = b_chunk[...]
    gain[s,...] = g_chunk[...]


h.close()