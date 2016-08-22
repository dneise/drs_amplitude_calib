# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import os
from astropy.io import fits
from tqdm import tqdm, trange
import numpy as np
from sklearn import linear_model, datasets
import h5py

plt.ion()
get_ipython().magic('matplotlib')

x = pd.HDFStore("all_drs_step2.h5")["all"].sort_values("temp_mean")
bsl = h5py.File("h5/bsl_gain.h5", "r")["bsl"]
chunk_N = bsl.chunks[-1]
T = (x.temp_mean - x.temp_mean.mean()).values

beta = np.zeros((1440, 1024), dtype='f8')
alpha = np.zeros((1440, 1024), dtype='f8')
SSE = np.zeros((1440, 1024), dtype='f8')

for j in trange(bsl.shape[-1]//chunk_N, leave=True):
    for k in trange(chunk_N):
        i = j*chunk_N + k
        if i >= bsl.shape[-1]:
            break

        foo = bsl[:,:,j*chunk_N:(j+1)*chunk_N]
        beta[:,i], alpha[:,i] = np.polyfit(T, foo[:,:,k], 1)
        hey = alpha[:,i] + T[:, None] * beta[:,i] - foo[:,:,k]
        SSE[:,i] = np.sqrt((hey**2).sum(axis=0))


res_f = h5py.File("h5/resis.h5", "w")
res_f.create_dataset("alpha", data=alpha)
res_f.create_dataset("beta", data=beta)
res_f.create_dataset("SSE", data=SSE)
