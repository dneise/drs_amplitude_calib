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

plt.figure()
plt.plot(T, bsl[:, 0, 0], '.', label="0, 0")
plt.plot(T, bsl[:, 30, 30], '.', label="30, 30")
plt.plot(T, bsl[:, 60, 60], '.', label="60, 60")
plt.plot(T, bsl[:, 3, 3], '.', label="3, 3")

def residual(p, c):
    return alpha[p,c] + T * beta[p,c] - bsl[:,p,c]

plt.figure()
plt.plot(T, residual(0, 0), '.', label="0, 0")
plt.plot(T, residual(30, 30), '.', label="30, 30")
plt.plot(T, residual(60, 60), '.', label="60, 60")
plt.plot(T, residual(3, 3), '.', label="3, 3")

