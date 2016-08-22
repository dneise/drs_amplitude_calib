# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import os
from astropy.io import fits
from tqdm import tqdm
import numpy as np
from sklearn import linear_model, datasets
import h5py

plt.ion()
get_ipython().magic('matplotlib')

x = pd.HDFStore("h5/all_drs_step2.h5")["all"].sort_values("temp_mean")
bsl = h5py.File("h5/bsl_gain.h5", "r")["bsl"]
alpha = h5py.File("h5/resis.h5", "r")["alpha"][...]
beta = h5py.File("h5/resis.h5", "r")["beta"][...]

T = (x.temp_mean - x.temp_mean.mean()).values

def residual(p, c):
	return alpha[p,c] + T * beta[p,c] - bsl[:,p,c]

foo = []
ts = []
for i in range(1024):
	foo.append(residual(300, i))
	ts.append(T)

foo = np.array(foo).flatten()
ts = np.array(ts).flatten()
plt.hist2d(ts, foo, cmap="viridis", bins=[100, 100])
