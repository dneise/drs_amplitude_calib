# coding: utf-8
import pandas as pd
import os
from astropy.io import fits
from tqdm import tqdm
import numpy as np
from sklearn import linear_model, datasets
import os.path

def download(src, dest, really=False):
    basename = os.path.basename(src)
    destname = os.path.join(dest, basename)
    if not os.path.isfile(destname):
        os.system("scp "+ src + " " + dest)

drs_runs = pd.HDFStore("all_drs_step2.h5")["all"]
path_temp = "isdc:/fact/raw/{y}/{m}/{d}/{n}_{r:03d}.drs.fits.gz"

for run in tqdm(drs_runs.itertuples()):
    n, r = run.fNight, run.fRunID
    n = str(n)
    y,m,d = n[0:4], n[4:6], n[6:8]
    download(path_temp.format(y=y, m=m, d=d, n=n, r=r), "./data/.", really=True)
