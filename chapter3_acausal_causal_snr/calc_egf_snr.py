#!/usr/bin/env python3
about = "This script calculates SNR values for acausal, causal, \
and symmetrized component of the original EGFs inside a directory."
usage = "Usage: python3 calc_egf_signal.py <EGF_dir> <out_file>"
# Coded By: omid.bagherpur@gmail.com
# Update: July 17, 2021
#=====Adjustable Parameters=====#
sac_path = "/usr/local/sac/bin/sac"  # path to SAC software
sacfile_regex = 'sac$'  # regular expression for sac files
signal_window_vel = [2, 4.5]
cut_max = 2000 # used for cutting symmetric signal for calculcation of signal times
min_signal_length = 50 # only used for very short inter-station paths (e.g., < 100 km)
#===============================#
# Code Block!

import os
import sys
os.system('clear')
print(f"{about}\n")

# import required modules
try:
    import re
    import subprocess
    import obspy
    import numpy as np
except ImportError as ie:
    print(f"{ie}\n\n")
    exit()

# check usage
if len(sys.argv) != 3:
    print(f"Error Usage!\n{usage}\n")
    exit()
else:
    egf_dir = os.path.abspath(sys.argv[1])
    out_file = os.path.abspath(sys.argv[2])

if not os.path.isdir(egf_dir):
    print(f"Error! Could not find the <egf_dir>!\n\n{usage}\n")
    exit()

###### CLASSES & FUNCTIONS ######

def get_egf_list(egf_dir):
    egf_list = []
    for x in os.listdir(egf_dir):
        if re.search(sacfile_regex,x):
            egf_list.append(os.path.join(egf_dir,x))
    return sorted(egf_list)


def get_sta_pairs(egf_list):
    sta_pairs = []
    for x in egf_list:
        try:
            sta1 = os.path.basename(x).split('_')[0]
            sta2 = os.path.basename(x).split('_')[1]
        except Exception as e:
            print(f"EGF filename format error!\n{e}\n")
            exit()
        sta_pairs.append([sta1, sta2])
    return sta_pairs


def get_sac_headers(egf):
    st = obspy.read(egf,format="SAC")
    sac_headers = st[0].stats.sac
    return sac_headers


def get_sac_data(egf):
    st = obspy.read(egf,format="SAC")
    return st[0].data


def get_sac_times(egf):
    headers = get_sac_headers(egf)
    times = np.arange(headers['b'],\
                      headers['e']+headers['delta'],\
                      headers['delta'])
    return times


def get_sac_data_in_range(egf, time_range):
    data = get_sac_data(egf)
    times = get_sac_times(egf)
    data_in_range = []
    for i in range(len(times)):
        if times[i] >= time_range[0] and times[i] <= time_range[1]:
            data_in_range.append(data[i])
    return data_in_range


def gen_sym_egf(inp_egf, sym_egf, sac_path, cut_max):
    shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0",\
                f"{sac_path}<<EOF"]
    shell_cmd.append(f'r {inp_egf}')
    shell_cmd.append('reverse')
    shell_cmd.append('w rev.tmp')
    shell_cmd.append(f'r {inp_egf}')
    shell_cmd.append('addf rev.tmp')
    shell_cmd.append('div 2')
    shell_cmd.append(f'w {sym_egf}')
    shell_cmd.append(f'cut 0 {cut_max}')
    shell_cmd.append(f'r {sym_egf}')
    shell_cmd.append(f'w {sym_egf}')  
    shell_cmd.append('quit')
    shell_cmd.append('EOF')
    shell_cmd = '\n'.join(shell_cmd)
    subprocess.call(shell_cmd, shell=True)
    os.remove('rev.tmp')


def calc_signal_times(sym_egf, signal_window_vel, min_signal_length):
    # Note: it's easier to find the envelope in symmetrized EGF, so sym_egf is required
    abs_data = np.abs(get_sac_data(sym_egf))
    abs_max_time = get_sac_times(sym_egf)[np.argmax(abs_data)]
    dist = float(get_sac_headers(sym_egf)['dist'])
    signal_len = dist/np.nanmin(signal_window_vel) -\
                 dist/np.nanmax(signal_window_vel)
    if signal_len < min_signal_length:
        signal_len = min_signal_length
    default_signal_center = dist/np.mean(signal_window_vel)
    t1 = int(abs_max_time - signal_len/2)
    if default_signal_center < t1 or default_signal_center > (t1+ signal_len):
        t1 = int(default_signal_center - signal_len/2)
    if t1 < 0:
        t1 = 0
    signal_times = [t1, t1+ signal_len]
    return signal_times


def calc_noise_times(signal_times):
    signal_len = signal_times[1] - signal_times[0]
    noise_times = [signal_times[1] + signal_len,
                   signal_times[1] + 2*signal_len]
    return(noise_times)


def calc_snr(signal, noise):
    srms = np.sqrt(np.nanmean(np.square(signal)))
    nrms = np.sqrt(np.nanmean(np.square(noise)))
    snr = 20*np.log10(srms/nrms)
    return snr

#################################

egf_list = get_egf_list(egf_dir)
if not len(egf_list):
    print(f"Error! Could not find any EGF in the given directory!\n{usage}\n")
    exit()

# egf_list = egf_list[0:3] # JUST FOR TEST!
sta_pairs = get_sta_pairs(egf_list)

# calculate and store SNR values for later output
sym_snr = []
causal_snr = []
acausal_snr = []
for i in range(len(egf_list)):
    print(f" {sys.argv[1]}, {sta_pairs[i][0]}_{sta_pairs[i][1]}; ({i+1} of {len(egf_list)})")
    sym_egf = f'{sta_pairs[i][0]}_{sta_pairs[i][1]}_sym.sac'
    gen_sym_egf(egf_list[i], sym_egf, sac_path, cut_max)
    # calculate signal/noise time range
    signal_times = calc_signal_times(sym_egf, signal_window_vel, min_signal_length)
    noise_times = calc_noise_times(signal_times)
    # calculate SNR for symmetrized EGF
    sym_signal_data = get_sac_data_in_range(sym_egf, signal_times)
    sym_noise_data = get_sac_data_in_range(sym_egf, noise_times)
    sym_snr.append(calc_snr(sym_signal_data, sym_noise_data))
    os.remove(sym_egf)
    # calculate SNR for causal signal
    causal_signal_data = get_sac_data_in_range(egf_list[i], signal_times)
    causal_noise_data = get_sac_data_in_range(egf_list[i], noise_times)
    causal_snr.append(calc_snr(causal_signal_data, causal_noise_data))
    # calculate SNR for acausal signal
    acausal_signal_data = get_sac_data_in_range(egf_list[i], [-1*signal_times[1],-1*signal_times[0]])
    acausal_noise_data = get_sac_data_in_range(egf_list[i], [-1*noise_times[1],-1*noise_times[0]])
    acausal_snr.append(calc_snr(acausal_signal_data, acausal_noise_data))


# start writting to output file
col_info = "sta1, sta2, az, baz, dist, nstack, acausal_snr, causal_snr, sym_snr"
print(f"\n\n Writting output: {out_file}\n\n Columns: {col_info}\n")
fopen = open(out_file,'w')
for i in range(len(egf_list)):
    headers = get_sac_headers(egf_list[i])
    # only output if all snr values are positive
    if acausal_snr[i] > 0 and causal_snr[i] > 0 and sym_snr[i] > 0:
	    fopen.write("%4s %4s %3.0f %3.0f %5.0f %5d %5.1f %5.1f %5.1f\n"\
              %(sta_pairs[i][0], sta_pairs[i][1], float(headers['az']),\
              float(headers['baz']), float(headers['dist']),\
              int(headers['kevnm']), float(acausal_snr[i]),\
              float(causal_snr[i]), float(sym_snr[i])))

fopen.close()
print("Done!\n")
