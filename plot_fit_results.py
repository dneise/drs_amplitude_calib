# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import os
from astropy.io import fits
from tqdm import tqdm, trange
import numpy as np
from sklearn import linear_model, datasets
import h5py

res_f = h5py.File("fit_results.h5")
plots = [
    (res_f["SSE"][...], "SSE", (None, None)),
    (res_f["alpha"][...], "alpha", (None, None)),
    (res_f["beta"][...], "beta", (None, None)),
]

for plot,plot_name,ylim in plots:
    plt.figure(figsize=(24, 18))
    m = plot.mean(axis=1)
    std = plot.std(axis=1)/np.sqrt(1024)
    fig, a = plt.subplots(4)
    for i in range(4):
        ax = a.flatten()[i]
        s = slice(i*1440//4, (i+1)*1440//4)
        ax.errorbar(x=np.arange(1440)[s], y=m[s], yerr=std[s], fmt=".--")
        s = slice(i*1440//4, (i+1)*1440//4 + 1)
        ticks = np.arange(0,1440+9)[s][::9]
        ax.set_xticks(ticks)
        ax.set_xlim(ticks[[0,-1]])
        ax.set_ylim(*ylim)
        ax.grid(True)
    plt.draw()
    plt.title(plot_name)
    plt.savefig(plot_name+".png")
    plt.close("all")