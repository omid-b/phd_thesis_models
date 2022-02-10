#!/usr/env/bin python3

# Coded by omid.bagherpur@gmail.com
# Update: July 19, 2021
#=====Adjustable Parameters=====#
angle_bin_size = 10
#===============================#
# Code Block!
import os
import sys
import numpy as np

os.system('clear')
if len(sys.argv) != 3:
    print(f"Usage: python3 fan_diagram_data.py <snr_data> <out_dir>\n\n")
    exit()

####### CLASSES & FUNCTIONS #######

def read_snr_data(orig_snr_file):
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
    try:
        fopen = open(orig_snr_file,'r')
        flines = fopen.readlines()
    except Exception as e:
        print(f"File is not available!\n{e}\n")
        exit()
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


def calc_uniq_list(inp_list):
    uniq_list = []
    for x in inp_list:
        if x not in uniq_list:
            uniq_list.append(x)
    return sorted(uniq_list)


def calc_angle_bins(angle_bin_size):
    angle_bins=[]
    angle_start = -(angle_bin_size/2)
    angle0 = angle_start
    angle1 = angle_start+angle_bin_size
    while angle1 != angle_start and angle1 != angle_start+360:       
        if (angle0+360) < 360:
            angle0=angle0+360
        elif (angle1+360) < 360:
            angle1=angle1+360
        angle_bins.append([angle0, angle1])
        angle0 = angle1
        angle1 = angle1+angle_bin_size
    if (angle_start+360) < 360:
            angle_start=angle_start+360
    angle_bins.append([angle0, angle_start])
    return angle_bins


def extract_station_snr_datasets(sta, sta1, sta2, az, baz, acausal_snr, causal_snr):
    nod = len(acausal_snr)
    angle = []
    snr = []
    for i in range(nod):
        if sta == sta1[i] or sta == sta2[i]:
            angle.append(baz[i])
            snr.append(causal_snr[i])
            angle.append(az[i])
            snr.append(acausal_snr[i])
    return angle, snr


def calc_fan_diagram_data(angle, snr, angle_bins):
    nbins = len(angle_bins)
    fan_diagram_data = [[] for x in range(nbins)]
    # the first angle bin has be calculated separately
    for x in range(len(angle)):
        if angle[x] >= angle_bins[0][0]\
         or angle[x] < angle_bins[0][1]\
         or angle[x] == 0:
            fan_diagram_data[0].append(snr[x])
    # now, calculte the remaining bins
    for i in range(1,nbins):
        for x in range(len(angle)):
            if angle[x] >= angle_bins[i][0] and angle[x] < angle_bins[i][1]:
                fan_diagram_data[i].append(snr[x])
    return fan_diagram_data

###################################

# read data; create output directory
sta1, sta2, az, baz, _, _, acausal_snr, causal_snr,_ = \
read_snr_data(sys.argv[1])
# uniq list of stations
stations = calc_uniq_list(sta1 + sta2)
nod = len(causal_snr) # number of data

if not os.path.isdir(sys.argv[2]):
    os.mkdir(sys.argv[2])

angle_bins = calc_angle_bins(angle_bin_size)
for sta in stations:
    print(sta)
    # calculate fan diagram data array
    angle, snr = extract_station_snr_datasets(sta, sta1, sta2, az, baz, acausal_snr, causal_snr)
    fan_diagram_data = calc_fan_diagram_data(angle, snr, angle_bins)
    # save calculated fan diagram to file
    fopen = open(os.path.join(sys.argv[2],f"fan_{sta}.dat"), 'w')
    for i in range(len(angle_bins)):
        if len(fan_diagram_data[i]):
            # angle-bin, #SNRs, std(SNRs), mean(SNRs)
            mean_snr = np.mean(fan_diagram_data[i])
            std_snr = "%6.2f" %(np.std(fan_diagram_data[i]))
            if len(fan_diagram_data[i]) == 1:
                std_snr = "%6s" %("N/A")
            fopen.write("%05.1f-%05.1f %3d %6s %6.2f\n" %(angle_bins[i][0], angle_bins[i][1], len(fan_diagram_data[i]), std_snr, mean_snr))
        else:
            fopen.write("%05.1f-%05.1f %3s %6s %6s\n" %(angle_bins[i][0], angle_bins[i][1], "N/A", "N/A", "N/A"))
    fopen.close()

print(f"\n\nColumns in output files are:\n  angle-bin, #SNRs, std(SNRs), mean(SNRs)\n\nDone!\n\n")

