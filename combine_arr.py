from __future__ import print_function

import tables as tb
import pandas as pd
import numpy as np
import argparse
import magic
import sys, os
from glob import glob

# ------------------------------------------------------------------------------
# combine_npz.py
# Combine numpy arrays from analyses over many files.
#
def get_parser(args=None):
    parser = argparse.ArgumentParser(description='Script to produce HDF5 files')
    parser.add_argument('-d','--dir',
                        action='store',
                        help='run number',
                        required='True')
    return parser

# get arguments
args = get_parser().parse_args()
opts = vars(args) # dict
npz_dir = args.dir

# input/output files
files = glob(npz_dir + '*.npz')
files = sorted(files, key=lambda s: int((s.split('_')[1])[:-4])) 
out_file = "{}/npz_combined.npz".format(npz_dir)

A_nelec = []; A_nrecomb = []; A_zlength = []

# check hdf5 file are completely written
for f in files:

    print("-- Adding file {}...".format(f))
    fn = np.load(f)

    if(len(fn['A_nelec']) == 0):
        print("WARNING: no data in file {}".format(f))
    else:
        A_nelec = np.concatenate((A_nelec,fn['A_nelec']))
        A_nrecomb = np.concatenate((A_nrecomb,fn['A_nrecomb']))
        A_zlength = np.concatenate((A_zlength,fn['A_zlength']))

    fn.close()

print("Saving combined file {}".format(out_file))
np.savez(out_file,
        A_nelec=A_nelec, A_nrecomb=A_nrecomb, A_zlength=A_zlength)
