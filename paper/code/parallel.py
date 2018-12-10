#!/usr/bin/python3

#SBATCH -N1 --exclusive

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import h5py
import tqdm
import emcee

from isochrones.mist import MIST_Isochrone
from isochrones import StarModel
mist = MIST_Isochrone()

import stardate as sd
from stardate.lhf import lnprob

from multiprocessing import Pool

# Necessary to add cwd to path when script run
# by SLURM (since it executes a copy)
sys.path.append(os.getcwd())

def infer_stellar_age(i):

    # Small observational uncertainties are needed (even though the stars
    # weren't simulated with any) in order to get a good fit.
    teff_err = 25  # Kelvin
    logg_err = .05  # dex
    feh_err = .05  # dex
    jmag_err = .01 # mags
    hmag_err = .01  # mags
    kmag_err = .01  # mags
    parallax_err = .05  # milliarcseconds
    prot_err = 1  # Days
    BV_err = .01  # mags

    # The directory where the posterior samples and result plots will be saved.
    savedir = "./iso_and_gyro"
    savedir_iso = "./iso_only"

    #  Infer ages of the simulated stars.

    # Set up the parameter dictionary.
    iso_params = {"teff": (df.teff[i], teff_err),
                "logg": (df.logg[i], logg_err),
                "feh": (df.feh[i], feh_err),
                "jmag": (df.jmag[i], jmag_err),
                "hmag": (df.hmag[i], hmag_err),
                "kmag": (df.kmag[i], kmag_err),
                "parallax": (df.parallax[i], parallax_err)}

    # Infer an age with isochrones and gyrochronology.

    # Set up the star object
    star = sd.star(iso_params, df.prot[i], .01, suffix="{0}_gyro".format(i))

    # Run the MCMC
    sampler = star.fit(max_n=200000)

    # Now infer an age with isochrones only.

    # Set up the star object
    star_iso = sd.star(iso_params, df.prot[i], .01, suffix="{0}_iso".format(i))

    # Run the MCMC
    sampler = star_iso.fit(max_n=200000, iso_only=True)


if __name__ == "__main__":
    #  Load the simulated data file.
    df = pd.read_csv("data/simulated_data.csv")
    N = len(df)

    p = Pool(24)
    p.map(infer_stellar_age, range(N))