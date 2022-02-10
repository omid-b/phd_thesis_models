#!/usr/bin/env python3
import os
import sys
about = "This script generates plots for the results of the LITMOD MCMC inversion directory."
usage = """
Usage:
python3 plot_LITMOD.py <inv_1> ... <inv_n> <outdir>

Notes: 1) <inv_1> to <inv_n> are the inversion results directories
       2) <outdir>: the output directory(will be generated if does
                    not exist)
"""
# Update: April 18, 2021
# Coded by: omid.bagherpur@gmail.com
#====Adjustable Parameters====#
figsize=(10,10)
seaborn_context = "notebook" # notebook, paper, talk, poster
seaborn_style = "ticks" # ticks, whitegrid, darkgrid, ...

# PDF interpolation parameters
pdf_interp_mesh_size = [300,300] # [vs_meshsize, depth_meshsize]
pdf_interp_method = 'linear' # linear, cubic, nearest
pdf_cmap_num_ticks = 50

# SUBPLOTS PARAMETERS
# PDF subplot parameters
cbar_padding = 0.06
cbar_ticks = 0.2
pdf_xlim = [2.9,5.2] # emply list for auto
pdf_ylim = [0,200] # emply list for auto
# Dispersion subplot parameters
disp_xlim = [] # emply list for auto
disp_ylim = [] # emply list for auto
# Moho thickness histogram subplot parameters
moho_xlim = [17,63] # emply list for auto
moho_ylim = [] # emply list for auto
#=============================#
# Code Block!
# os.system('clear')
print(f"{about}\n")

# reference models
AK135_vs_vs = [3.460,3.460,3.850,3.850,4.480,4.490,4.500,4.509,4.518,4.523,4.609,4.696,4.783,4.870,5.080,5.186,5.292,5.398,5.504]
AK135_vs_depth = [0.0,20.0,20.0,35.0,35.0,77.5,120.0,165.0,210.0,210.0,260.0,310.0,360.0,410.0,410.0,460.0,510.0,560.0,610.0]
AK135_phv_prd = [3,4,5,6,7,8,9,10,11,12,14,16,18,20,22,25,27,30,32,34,36,38,40,42,45,47,50,52,55]
AK135_phv_phv = [3.1729,3.1734,3.1754,3.1803,3.1889,3.2014,3.2180,3.2386,3.2627,3.2903,3.3545,3.4277,3.5055,3.5823,3.6534,3.7430,3.7907,3.8469,3.8763,3.9007,3.9213,3.9390,3.9543,3.9678,3.9854,3.9959,4.0101,4.0189,4.0312]

# import required modules
try:
	import numpy as np
	from glob import glob
	import seaborn as sns
	import matplotlib as mpl
	import matplotlib.pyplot as plt
	from scipy.interpolate import griddata
except ImportError as ie:
	print(f"{ie}\n")
	exit()

# check usage
if len(sys.argv) < 3:
	print(f"{usage}\n")
	exit()
else:
	outdir = os.path.abspath(sys.argv[-1])
	invdirs = []
	for i in range(1,len(sys.argv)-1):
		invdirs.append(os.path.abspath(sys.argv[i]))

# read input dispersion data
periods = []
phvels = []
errors = []
for invdir in invdirs:
	disp = os.path.join(invdir,f"{os.path.basename(invdir)}.dat")
	if os.path.isfile(disp):
		fopen = open(disp, 'r')
		flines = fopen.readlines()
		for i in range(1,len(flines)-1):
			periods.append(int(flines[i].split("\n")[0].split()[3]))
			phvels.append(float(flines[i].split("\n")[0].split()[4]))
			errors.append(float(flines[i].split("\n")[0].split()[5]))
	else:
		print(f"Error! Could not find dispersion file: '{os.path.basename(disp)}'\n")
		exit()

# read output Moho solutions
moho_sols = []
for invdir in invdirs:
	moho_file = os.path.join(invdir,'moho.lst')
	if os.path.isfile(moho_file):
		moho_vals = np.loadtxt(moho_file,unpack=True,dtype=float)
		moho_sols.append(moho_vals)

# read and interpolate PDF data
pdf_x, pdf_y, pdf_z = [], [], []
for invdir in invdirs:
	mean_prob_dep, mean_prob_vel, _, _, _ = np.loadtxt(os.path.join(invdir,'mean_prob.lst'),
		                                               unpack=True,dtype=float)
	max_prob_dep, max_prob_vel, _, _, _ = np.loadtxt(os.path.join(invdir,'max_prob.lst'),
		                                             unpack=True,dtype=float)
	pdf_sols = os.path.join(invdir,'proCr.lst')
	c1, c2, c3 = np.loadtxt(pdf_sols, unpack=True, dtype=float)
	xy, z = [], []
	for ic in range(len(c1)):
		xy.append([c1[ic], c2[ic]])
		z.append(c3[ic])
	c1_grd_nods = np.linspace(np.nanmin(c1), np.nanmax(c1), pdf_interp_mesh_size[0])
	c2_grd_nods = np.linspace(np.nanmin(c2), np.nanmax(c2), pdf_interp_mesh_size[1])
	xm, ym = np.meshgrid(c1_grd_nods,c2_grd_nods) 
	grd = griddata(np.array(xy),np.array(z), (xm,ym), method=pdf_interp_method)

	# plot script
	sns.set_style(seaborn_style)
	sns.set_context(seaborn_context)
	f = plt.figure(figsize=figsize)
	# Subplot1: PDF
	ax1 = plt.subplot2grid((12,11), (1,1), rowspan=11, colspan=4)
	plt.title("Posterior probability")
	cmap = mpl.cm.hot
	bounds = np.linspace(0,1,pdf_cmap_num_ticks)
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	plt.pcolormesh(xm,ym,grd,cmap=cmap, norm=norm, shading="auto", rasterized="True")
	plt.plot(AK135_vs_vs,AK135_vs_depth,
		     color='g', linewidth=3,
             linestyle=(0, (4, 2, 1, 2)),
             dash_capstyle='round',label='AK135')
	plt.plot(max_prob_vel,max_prob_dep,linewidth=3,color="#8E44AD",label='Max PDF')
	plt.plot(mean_prob_vel,mean_prob_dep,linewidth=3,color="#3498DB",label='Mean PDF')
	plt.legend(loc='lower left')
	if len(pdf_xlim):
		plt.xlim(pdf_xlim)
	if len(pdf_ylim):
		plt.ylim(pdf_ylim)
	plt.xlabel('Vs (km/s)')
	plt.ylabel('Depth (km)')
	cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
		                orientation='horizontal', label='Posterior PDF',
		                ticks=np.arange(0,1+cbar_ticks,cbar_ticks),
		                pad=cbar_padding)
	ax1.invert_yaxis()
	# Subplot2: Dispersions
	ax2 = plt.subplot2grid((12,11), (1,5), rowspan=4, colspan=5)
	plt.title("Inversion input/output dispersion curves")
	invDisps = glob(f"{invdir}/pCr*.dat")
	for idsp in range(len(invDisps)):
		prd, phv, _ = np.loadtxt(invDisps[idsp],unpack=True,dtype=float)
		if idsp == 0:
			plt.plot(prd,phv,zorder=1,color=(0.7,0.7,0.7),label="Inversion dispersion data")
		else:
			plt.plot(prd,phv,zorder=1,color=(0.7,0.7,0.7))
	plt.plot(AK135_phv_prd,AK135_phv_phv,zorder=1,
		     label="AK135",color='g',linewidth=3,
             linestyle=(0, (4, 2, 1, 2)),
             dash_capstyle='round')
	plt.errorbar(periods,phvels,yerr=errors,marker='o', ms=3, mew=2,
		         ls="None",zorder=2, label="Input dispersion data",capsize=3)
	plt.legend(loc='lower right')
	plt.xlabel('Period (s)')
	plt.ylabel('Phase velocity (km/s)')
	if len(disp_xlim):
		plt.xlim(disp_xlim)
	if len(disp_ylim):
		plt.ylim(disp_ylim)
	# Subplot3: Moho depths
	ax3 = plt.subplot2grid((12,11), (6,5), rowspan=4, colspan=5)
	plt.title("Moho depth solutions")
	plt.hist(moho_sols[0])
	plt.xlabel('Moho depth (km)')
	plt.ylabel('Count')
	if len(moho_xlim):
		plt.xlim(moho_xlim)
	if len(moho_ylim):
		plt.ylim(moho_ylim)
	plt.tight_layout(pad=0, w_pad=0.5, h_pad=1.0)
	#plt.show()
	savefig = f"{os.path.basename(invdirs[0])}.pdf"
	print(savefig)
	plt.savefig(savefig,dpi=300,transparent=True)
	plt.close()

