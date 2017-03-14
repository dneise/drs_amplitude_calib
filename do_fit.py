# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import os
from astropy.io import fits
from tqdm import tqdm, trange
import numpy as np
from sklearn import linear_model
import h5py

x = pd.read_hdf("all_drs_step2.h5")
bsl = h5py.File("bsl.h5", "r")["bsl"]
chunk_N = bsl.chunks[-1]
res_f = h5py.File("fit_results.h5", "w")

beta = res_f.create_dataset("beta", shape=(1440, 1024), dtype='f8')
alpha = res_f.create_dataset("alpha", shape=(1440, 1024), dtype='f8')
SSE = res_f.create_dataset("SSE", shape=(1440, 1024), dtype='f8')

N_cells = bsl.shape[-1]

for cell_chunk_id in trange(N_cells//chunk_N, leave=True):
    cell_slice=slice(cell_chunk_id * chunk_N, (cell_chunk_id + 1) * chunk_N)

    bsl_chunk = bsl[:, :, cell_slice]
    for chip_id in range(160):
        T = x["drs_T_{0:03d}".format(chip_id)].values
        for cell_in_chunk in range(chunk_N):
            cell_id = cell_in_chunk + cell_chunk_id * chunk_N

            if cell_id >= N_cells:
                break

            p_slice=slice(chip_id*9, (chip_id+1)*9)


            fit = np.polyfit(T, bsl_chunk[:, p_slice, cell_in_chunk], deg=1)
            beta[p_slice, cell_id], alpha[p_slice, cell_id] = fit

            resi = alpha[p_slice, cell_id] + T[:, None] * beta[p_slice, cell_id] - bsl_chunk[:, p_slice, cell_in_chunk]
            SSE[p_slice, cell_id] = np.sqrt((resi**2).sum(axis=0))
