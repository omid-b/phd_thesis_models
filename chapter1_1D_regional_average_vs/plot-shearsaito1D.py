#!/usr/bin/env python3
'''
This script generates plots for the output model of the shearsaito code.

USAGE: ./plot-shearsaito1D.py <shearsaito output (e.g. 'shvel.d')>  <stmodel.d>

Coded by: Omid.bagherpur@gmail.com
UPDATE: 5 March 2019
'''
#=====Adjustable Parameters=====#
#Figure style:
output_filetype = 'pdf'
depthTick= 20
vsTick   = 0.25
legSize  = 11 #legend font size
figSize  = (12,8) # Size of the figure along (x, y) axis
context  = "notebook" ;# seaborn set_context: notebook, talk, poster, paper
style    = "whitegrid" ; # seaborn styles: darkgrid, whitegrid, white, ticks ...

#Resolution matrix plot:
plot_rows = 'y' # 'y' or 'n'
depth_index = [7,11,15,19]
text_offset = [0.01, 8]
#===============================#
#Code block!
import sys,os
os.system('clear')
print("This script generates plots for the output model of the shearsaito code.\n")
if len(sys.argv) != 4:
	print("  USAGE: ",sys.argv[0]," <shvel.d> <resolution.d> <stmodel.d> \n")
	exit()

#Import the required modules:
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns
#--------------------------

shvelfile = sys.argv[1]
resfile   = sys.argv[2]
stmfile   = sys.argv[3]

#find main results
i=0
for line in open(shvelfile,mode='r'):
	i+=1
	if 'main' in line:
		ln_main= i
	if 'data' in line:
		ln_data= i
	if 'residuals' in line:
		ln_residuals= i
	if 'damp' in line:
		ln_damp= i


nlayer = int((ln_data-ln_main-1)/2) #number of layers
nper   = int(ln_damp-ln_residuals-1) #number of periods

#read data: main results
depth = np.empty(nlayer*2);
thick = np.empty(nlayer*2); rho = np.empty(nlayer*2);
vp = np.empty(nlayer*2); vs = np.empty(nlayer*2);
with open(shvelfile,mode='r') as data:
	i=0; sum1=0;
	for line in itertools.islice(data, ln_main, ln_data-1):
		thick[i], rho[i], vp[i], vs[i]= line.split()
		sum1=sum1+thick[i]
		depth[i]=sum1
		i+=1

#moho= depth[5]; for 3 crustal layers

i=1; v=vs[2*i-1]
while (v < 4):
  i+=1
  v=vs[2*i-1]

moho=  depth[2*i-2]
  

with open(shvelfile,mode='r') as data:
	for line in itertools.islice(data, ln_damp-1, ln_damp):
		dmp=round(float(line.split()[1]), 4)

#read data: residuals
period = np.zeros(nper)
observed = np.zeros(nper)
synthetic = np.zeros(nper)
residuals = np.zeros(nper)
with open(shvelfile,mode='r') as data:
	i=0
	for line in itertools.islice(data, ln_residuals, ln_damp-1):
		period[i], observed[i], synthetic[i], residuals[i]= line.split()
		i+=1


#read stmodel 
i=0
for line in open(stmfile,mode='r'):
	i+=1
	if i==4:
		stm_nlayer = int(int(line.split()[0])/2);
		break

stm_depth = np.empty(stm_nlayer*2);
stm_thick = np.empty(stm_nlayer*2); stm_rho = np.empty(stm_nlayer*2);
stm_vp = np.empty(stm_nlayer*2); stm_vs = np.empty(stm_nlayer*2);
with open(stmfile,mode='r') as stm:
	i=0; sum1=0;
	for line in itertools.islice(stm, 5, 5+(stm_nlayer*2)):
		stm_thick[i], stm_rho[i], stm_vp[i], stm_vs[i]= line.split()
		sum1=sum1+stm_thick[i]
		stm_depth[i]=sum1
		i+=1

mid_depth = np.empty(int(len(depth)/2))
i2=0
for i in range(0,len(depth)-2,2):
   mid_depth[i2]=(depth[i+1]-depth[i])/2 + depth[i]
   i2+=1



#read resolution file
c1=np.empty(5000)
c2=np.empty(5000)
c3=np.empty(5000)
res_diag= np.empty([100, 2])


i=0
i2=0
for line in open(resfile,mode='r'):
	i+=1
	c1[i], c2[i], c3[i] = line.split()
	if i>1:
	  if c1[i]==c2[i] and float(c1[i])!=0:
	    res_diag[i2:]= [float(c1[i]), float(c3[i])]
	    i2+=1

#make a clean reslolution matrix:
nres=i
resMatrix=[]
for i1 in range(nlayer-1):
  for i2 in range(nres):
    if ( mid_depth[i1] == c1[i2] and float(c2[i2]) != 0):
      resMatrix.append([c1[i2], c2[i2], c3[i2]])
      
resMatrix=np.array(resMatrix).reshape((nlayer-1,nlayer-1, 3))


#plot 1 of 2 (shear wave velocity profile):
sns.set(style=style)
sns.set_context(context)
plt.figure(1,figSize)
gs = gridspec.GridSpec(1, 2, width_ratios=[0.45, 1]) 

ax1 = plt.subplot(gs[0])
plt.plot(stm_vs, stm_depth,label='Starting model');
invLabel= f'Inversion results\n(dmp= {dmp}, CT= {moho}km)'
plt.plot(vs, depth,label=invLabel);
plt.yticks(range(0, 1000, depthTick))
plt.xticks(np.arange(2.5, 7, vsTick))
plt.ylim((0,250))
#plt.xlim((min(vs)-0.1, max(vs)+0.1))
plt.xlim((3.4, 5))
plt.gca().invert_yaxis();

plt.xlabel('Vs (km/s)')
plt.ylabel('Depth (km)')
plt.legend(loc='lower left', prop={'size':legSize})

ak135_per = [ 19.1402, 20.0784, 21.1134, 22.0215, 23.0112, 24.0941, 25.2840, 26.2564, 27.3067, 28.0548, 29.2571, 30.1176, 31.0303, 32.0000, 33.0323, 34.1333, 35.3103, 36.5714, 37.2364, 38.6415, 39.3846, 40.1569, 41.7959, 42.6667, 43.5745, 44.5217, 45.5111, 46.5454, 47.6279, 48.7619, 49.9512, 51.2000, 52.5128, 53.8947, 55.3513, 56.8889, 58.5143, 60.2353, 62.0606, 64.0000, 66.0645, 68.2667, 70.6207, 73.1429, 75.8519, 78.7692, 81.9200, 85.3333, 89.0435, 93.0909, 97.5238, 102.4000, 107.7895, 113.7778, 120.4706, 128.0000, 136.5333, 146.2857, 157.5385, 170.6667, 186.1818, 204.8000]
ak135_vph = [3.5548, 3.5900, 3.6273, 3.6582, 3.6898, 3.7217, 3.7534, 3.7768, 3.7998, 3.8148, 3.8366, 3.8508, 3.8645, 3.8779, 3.8909, 3.9035, 3.9157, 3.9275, 3.9333, 3.9446, 3.9501, 3.9556, 3.9664, 3.9717, 3.9769, 3.9821, 3.9873, 3.9925, 3.9977, 4.0028, 4.0080, 4.0133, 4.0185, 4.0239, 4.0293, 4.0349, 4.0406, 4.0464, 4.0525, 4.0588, 4.0654, 4.0723, 4.0796, 4.0874, 4.0957, 4.1048, 4.1145, 4.1252, 4.1371, 4.1502, 4.1650, 4.1818, 4.2009, 4.2231, 4.2490, 4.2797, 4.3165, 4.3612, 4.4161, 4.4848, 4.5718, 4.6832]

ax2 = plt.subplot(gs[1])
plt.plot(ak135_per, ak135_vph,label='AK135',color='gray',linestyle='--');
plt.scatter(period, observed,label='Observed',color='red',marker='^');
plt.plot(period, synthetic,label='Synthetic');



plt.xlabel('Period (s)')
plt.ylabel('Phase velocity (km/s)')
plt.yticks(np.arange(round(min(observed)-0.05,1), round(max(observed)+0.2,1), 0.1))
plt.legend(loc='best', prop={'size':legSize})

plt.ylim((3.55,4.5))
plt.xlim((10,175))

plt.tight_layout()
figout = f'{sys.argv[1]}.{output_filetype}'
plt.savefig(figout,dpi=300,transparent=True)
print(f"{figout} is created!")
#plt.show()


#plot 2 of 2 (resolution matrix):
sns.set(style=style)
sns.set_context(context) 
newFigSize = (figSize[1]*0.5, figSize[1]) #aspect ratio of the plot
plt.figure(2,newFigSize)

plt.plot(res_diag[0:i2,1], res_diag[0:i2,0],label=" Resolution Matrix\n(diagonal elements)");


if ( plot_rows == 'y' ):
  for i in depth_index:
    plt.plot(resMatrix[i,:,2], resMatrix[i,:,1],color='gray', linestyle=':')
    plt.text(resMatrix[i,i,2]+text_offset[0], resMatrix[i,i,1]+text_offset[1], str(int(resMatrix[i,i,1]))+' km', fontdict=None, withdash=False)
    
plt.scatter(res_diag[0:i2,1], res_diag[0:i2,0])


plt.xticks(np.arange(-0.1, 1.01, 0.1))
plt.yticks(range(0, 1000, depthTick))
plt.ylim((0,400))
plt.xlim((-0.07, 0.30))
plt.gca().invert_yaxis();

plt.xlabel(' ')
plt.ylabel('Depth (km)')
plt.legend(loc='lower right', prop={'size':legSize})

plt.tight_layout()
figout = f'{sys.argv[2]}.{output_filetype}'
plt.savefig(figout,dpi=300,transparent=True)
print(f"{figout} is created!")
