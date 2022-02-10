#!/usr/bin/env python3

import os
import sys
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import shutil

usage = "Usage: python3 plot_fan_diagram.py <fan_datalist> <out_dir> <max_snr> <max_rstd>"
os.system('clear')
if len(sys.argv) != 5:
    print(f"{usage}\n\n")
    exit()
    
#====Adjustable Parameters=====#
max_snr = float(sys.argv[3])
max_rstd = float(sys.argv[4])
# max_std = 5
#==============================#


##### FUNCTIONS #####

def read_fan_datalist(datalist):
    try:
        fopen = open(datalist, 'r')
        flines = fopen.readlines()
        fopen.close()
        fan_datalist = []
        for x in flines:
            fan_datalist.append(x.split('\n')[0])
    except Exception as e:
        print(f"Datalist read error!\n{e}\n")
        exit()
    return fan_datalist


def read_fan_data(fan_data):
    try:
        angle_bin, count, std, snr = np.loadtxt(fan_data, unpack=True, dtype=str)
    except Exception as e:
        print(f"Error! Could not read fan_data: {fan_data}\n{e}\n\n")
        exit()
    return angle_bin, count, std, snr


def get_angle_bin_size(angle_bin):
    angle1 = angle_bin[-1].split('-')[0]
    angle2 = angle_bin[-1].split('-')[1]
    angle_bin_size = float(angle2)-float(angle1)
    return angle_bin_size

def is_data(data):
    is_data = []
    for i in range(len(data)):
        if data[i] == "N/A":
            is_data.append(0)
        else:
            is_data.append(1)
    return is_data


def plot_fan_diagram_pdf(out_pdf, is_data, data, max_value, std_plot=False):
    data = np.array(data, dtype=float)
    angle_bin_size = 360 / len(is_data)
    angle_bin_centres = np.arange(0, 360, angle_bin_size)
    sns.set_context("notebook")
    f = plt.figure(figsize=(6,8))
    ax1=plt.subplot2grid((50,50), (0, 3),rowspan=48, colspan=46, projection='polar')
    ax1.set_theta_zero_location("N")
    ax1.set_theta_direction(-1)
    ax1.set_xticks(np.deg2rad([0,90,180,270]))
    plt.yticks([],[])
    plt.margins(0)
    i = 0
    bars=ax1.bar(np.deg2rad(angle_bin_centres), is_data, bottom=0,width=np.deg2rad(angle_bin_size))
    for bar in bars:
        bar.set_color(get_snr_rgba(data[i], max_value, std_plot))
        bar.set_edgecolor((0,0,0,1))
        i += 1
    ax2=plt.subplot2grid((50,50), (34, 0),rowspan=15, colspan=1)
    if std_plot:
        cmap = mpl.cm.cool
    else:
        cmap = mpl.cm.jet
    norm = mpl.colors.Normalize(vmin=0, vmax=max_value)
    ax2 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='vertical')
    # plt.tight_layout()
    plt.savefig(out_pdf, dpi=300, transparent=True, format="PDF")
    plt.close()


def plot_fan_diagram_png(out_png, is_data, data, max_value, std_plot=False):
    data = np.array(data, dtype=float)
    angle_bin_size = 360 / len(is_data)
    angle_bin_centres = np.arange(0, 360, angle_bin_size)
    sns.set_context("notebook")
    f = plt.figure(figsize=(10,10))
    ax1=plt.subplot2grid((50,50), (0, 0), rowspan=50, colspan=50, projection='polar')
    ax1.set_theta_zero_location("N")
    ax1.set_theta_direction(-1)
    plt.xticks([],[])
    plt.yticks([],[])
    ax1.set_ylim(0,1)
    plt.margins(0)
    i = 0
    bars=ax1.bar(np.deg2rad(angle_bin_centres), is_data, bottom=0,width=np.deg2rad(angle_bin_size))
    for bar in bars:
        bar.set_color(get_snr_rgba(data[i], max_value, std_plot))
        bar.set_edgecolor((0,0,0,0))
        i += 1
    ax1.spines['polar'].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, transparent=True, format="PNG")
    plt.close()


def get_snr_rgba(value, maxValue, std_plot=False):
    if std_plot:
        return plt.cm.cool((np.clip(value,0,maxValue))/maxValue)
    else:
        return plt.cm.jet((np.clip(value,0,maxValue))/maxValue)


#####################

fan_datalist = read_fan_datalist(sys.argv[1])
out_dir = sys.argv[2]

# make output directory if does not exist
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)


max_snr_array = []
max_std_array = []
max_rstd_array = []

for fan_data in fan_datalist:
    print(f"  fan_data: {fan_data}")
    # output file names
    basename = '.'.join(os.path.basename(fan_data).split('.')[0:-1])
    pdf_snr = os.path.join(out_dir, f"snr_{basename}.pdf")
    pdf_std = os.path.join(out_dir, f"std_{basename}.pdf")
    pdf_rstd = os.path.join(out_dir, f"rstd_{basename}.pdf")
    png_snr = os.path.join(out_dir, f"snr_{basename}.png")
    png_std = os.path.join(out_dir, f"std_{basename}.png")
    png_rstd = os.path.join(out_dir, f"rstd_{basename}.png")
    # fan-diagram data processing
    angle_bin, count, std, snr = read_fan_data(fan_data)
    is_std = is_data(std)
    is_snr = is_data(snr)
    # generate final data for plotting ("N/A" > -999)
    rstd = []
    for i in range(len(angle_bin)):
        # modify snr for plotting
        if is_snr[i] == False:
            snr[i] = -999 # a dummy value; will do the trick!
        # modify std for plotting, calculate rstd
        if is_std[i]:
            # std[i] =  float(std[i])
            rstd.append((float(std[i])/float(snr[i]))*100)
        else:
            std[i] = -999 # a dummy value; will do the trick!
            rstd.append(-999)
    # find maximum value of the datasets
    snr = np.array(snr, dtype=float)
    std = np.array(std, dtype=float)
    rstd = np.array(rstd, dtype=float)
    max_snr_array.append(np.nanmax(snr))
    max_std_array.append(np.nanmax(std))
    max_rstd_array.append(np.nanmax(rstd))
    # save plots
    plot_fan_diagram_pdf(pdf_snr, is_snr, snr, max_snr)
    # plot_fan_diagram_pdf(pdf_std, is_std, std, max_std, std_plot=True)
    plot_fan_diagram_pdf(pdf_rstd, is_std, rstd, max_rstd, std_plot=True)
    plot_fan_diagram_png(png_snr, is_snr, snr, max_snr)
    plot_fan_diagram_png(png_rstd, is_std, rstd, max_rstd, std_plot=True)
    # plot_fan_diagram_png(png_std, is_std, std, max_std, std_plot=True)


txt1 = "%18s %6s %6s %6s" %("min", "max", "median", "std")
txt2 = " Max SNRs:  %6.2f %6.2f %6.2f %6.2f" %(np.nanmin(max_snr_array), np.nanmax(max_snr_array), np.nanmedian(max_snr_array), np.nanstd(max_snr_array)) 
txt3 = " Max RSTDs: %6.2f %6.2f %6.2f %6.2f" %(np.nanmin(max_rstd_array), np.nanmax(max_rstd_array), np.nanmedian(max_rstd_array), np.nanstd(max_rstd_array)) 
txt4 = " Max STDs:  %6.2f %6.2f %6.2f %6.2f" %(np.nanmin(max_std_array), np.nanmax(max_std_array), np.nanmedian(max_std_array), np.nanstd(max_std_array)) 
print(f"\n{txt1}\n{txt2}\n{txt3}\n{txt4}\n")

fopen = open(os.path.join(out_dir,'README.txt'), 'w')
fopen.write(f"{txt1}\n{txt2}\n{txt3}\n{txt4}\n")
fopen.close()
shutil.copyfile(sys.argv[1], os.path.join(out_dir, os.path.basename(sys.argv[1])))


print("\nDone!\n")
