# coding: utf-8
import pandas as pd
import os
from astropy.io import fits
from tqdm import tqdm, trange
import numpy as np
import h5py

df = pd.read_hdf("all_drs_step2.h5")
if os.path.isfile("bsl.h5"):
    os.unlink("bsl.h5")

h = h5py.File("bsl.h5")
chunk_N = 32
bsl = h.create_dataset(
    "bsl",
    shape=(len(df), 1440, 1024),
    dtype=np.int16,
    fillvalue=np.nan,
    chunks=(chunk_N, 1440, 32)
)

for chunk_id in trange(len(df)//chunk_N + 1):
    b_chunk = np.ones(
        (chunk_N, 1440, 1024),
        dtype=np.int16
    ) * np.nan

    for i in range(chunk_N):
        run_id = chunk_id * chunk_N + i
        try:
            run = df.iloc[run_id]
        except IndexError:
            break

        path = "/fact/raw/{y:04d}/{m:02d}/{d:02d}/{n}_{r:03d}.drs.fits.gz".format(
            y=n // 10000,
            d=n % 100,
            m=(n // 100) % 100,
            n=run.fNight,
            r=run.fRunID
        )

        try:
            with fits.open(path) as f:
                b = f[1].data["BaselineMean"].reshape(1440, -1)
                b *= 4096/2000
                b *= 4

                b = b.round().astype(np.int16)
                b_chunk[i, ...] = b[...]
        except FileNotFoundError:
            print(path, "not found")
            pass

    s = slice(chunk_id*chunk_N, (chunk_id+1) * chunk_N)
    try:
        bsl[s,...] = b_chunk[...]
    except:
        pass
bsl[s,...] = b_chunk[:i,...]

h.close()