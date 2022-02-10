#!/usr/bin/env python3

about = "This script reads previously calculated snr ascii data file,\
 and corrects the values for reference values for the stack number and distance."
usage = "Usage: python3 correct_egf_snr.py <inp_snr_orig>  <out_dir>"

# Coded by: omid.bagherpur@gmail.com
# Update: July 18, 2021
#====Adjustable Parameters====#
manual_ref_dist = [False, 500] # if True, reference distance is set manually
manual_ref_nstack = [False, 30] # if True, reference num_stack is set manually
#=============================#
# Code Block!

import os
import sys
os.system('clear')
print(f"{about}\n")

# import required modules
try:
    import shutil
    import numpy as np
except ImportError as ie:
    print(f"{ie}")
    exit()

if len(sys.argv) != 3:
    print(f"Error usage!\n{usage}\n")
    exit()
else:
    orig_snr_file = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])

if not os.path.isfile(orig_snr_file):
    print(f"Error! Could not find the input SNR data file!\n")
    exit()


####### CLASSES & FUNCTIONS #######

def read_snr_orig(orig_snr_file):
    # initialize lists
    sta1 = []
    sta2 = []
    az = []
    baz = []
    dist = []
    nstack = []
    acausal_snr = []
    causal_snr = []
    sym_snr = []
    # read file
    fopen = open(orig_snr_file,'r')
    flines = fopen.readlines()
    fopen.close()
    for line in flines:
        line = line.split('\n')[0]
        try:
            cols = line.split()
            sta1.append(cols[0])
            sta2.append(cols[1])
            az.append(int(cols[2]))
            baz.append(int(cols[3]))
            dist.append(int(cols[4]))
            nstack.append(int(cols[5]))
            acausal_snr.append(float(cols[6]))
            causal_snr.append(float(cols[7]))
            sym_snr.append(float(cols[8]))
        except Exception as e:
            print(f"Input file format error!\n{e}\n")
            exit()
    return sta1,sta2,az,baz,dist,nstack,\
           acausal_snr,causal_snr,sym_snr


def correct_snr_dist(snr, dist, ref_dist):
    corr_fact = np.sqrt(dist/ref_dist)
    return snr*corr_fact


def correct_snr_nstack(snr, nstack, ref_nstack):
    corr_fact = np.sqrt(ref_nstack/nstack)
    return snr*corr_fact


def correct_snr_all(snr, dist, ref_dist, nstack, ref_nstack):
    corr_fact = np.sqrt(dist/ref_dist) * np.sqrt(ref_nstack/nstack)
    return snr*corr_fact

###################################

# read data
sta1,sta2,az,baz,dist,nstack,acausal_snr,causal_snr,sym_snr = \
read_snr_orig(orig_snr_file)

nol = len(sta1)

# reference dist and nstack
ref_dist = np.median(dist)
if manual_ref_dist[0]:
	ref_dist = manual_ref_dist[1]

ref_nstack = np.median(nstack)
if manual_ref_nstack[0]:
	ref_nstack = manual_ref_nstack[1]


# create output directory if does not exist
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

# outpuf file names
basename = '.'.join(os.path.basename(orig_snr_file).split('.')[0:-1])
fname_info = os.path.join(out_dir,f"{basename}_info.dat")
fname_corr_all = os.path.join(out_dir,f"{basename}_corr_all.dat")
fname_corr_dist = os.path.join(out_dir,f"{basename}_corr_dist.dat")
fname_corr_nstack = os.path.join(out_dir,f"{basename}_corr_nstack.dat")

# print info to standard output and info file
col_info = "sta1, sta2, az, baz, dist, nstack, acausal_snr, causal_snr, sym_snr"
print(f"\n\n Writting outputs for: '{basename}.dat'\n\n Columns: {col_info}\n")
fopen = open(fname_info, 'w')
fopen.write("Columns: %s\n\nReference distance: %.0f\nReference nStack: %.0f\n" %(col_info, ref_dist, ref_nstack))
fopen.close()


# output corrected all (dist + nstack)
fopen = open(fname_corr_all,'w')
for i in range(nol):
    fopen.write("%4s %4s %3d %3d %5d %5d %5.1f %5.1f %5.1f\n" \
    %(sta1[i],sta2[i],az[i],baz[i],dist[i],nstack[i],\
    correct_snr_all(acausal_snr[i], dist[i], ref_dist, nstack[i], ref_nstack),\
    correct_snr_all(causal_snr[i], dist[i], ref_dist, nstack[i], ref_nstack),\
    correct_snr_all(sym_snr[i], dist[i], ref_dist, nstack[i], ref_nstack)))
fopen.close()


# output corrected for distance only
fopen = open(fname_corr_dist,'w')
for i in range(nol):
    fopen.write("%4s %4s %3d %3d %5d %5d %5.1f %5.1f %5.1f\n" \
    %(sta1[i],sta2[i],az[i],baz[i],dist[i],nstack[i],\
    correct_snr_dist(acausal_snr[i], dist[i], ref_dist),\
    correct_snr_dist(causal_snr[i], dist[i], ref_dist),\
    correct_snr_dist(sym_snr[i], dist[i], ref_dist)))
fopen.close()


# output corrected for nstack only
fopen = open(fname_corr_nstack,'w')
for i in range(nol):
    fopen.write("%4s %4s %3d %3d %5d %5d %5.1f %5.1f %5.1f\n" \
    %(sta1[i],sta2[i],az[i],baz[i],dist[i],nstack[i],\
    correct_snr_nstack(acausal_snr[i], nstack[i], ref_nstack),\
    correct_snr_nstack(causal_snr[i], nstack[i], ref_nstack),\
    correct_snr_nstack(sym_snr[i], nstack[i], ref_nstack)))
fopen.close()

# copy the original in the output directory
shutil.copyfile(orig_snr_file, os.path.join(out_dir,f'{basename}.dat'))

print("Done!\n")


