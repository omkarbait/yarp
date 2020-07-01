'''
Script for take a basic look at the data and to identify and flag bad/non-working antennas. 
'''
import os
import yaml
import casatasks as cts
import parameters as prms
import subprocess

params = prms.read('parameters.yaml')

general_params = params['general'] # loading general params
msfile = general_params['msfile']
outdir = general_params['outdir']
fluxcal= general_params['fluxcal']

try:
	os.system('mkdir ' + outdir)
	os.system('mkdir ' + outdir+'listscan/')
except:
	None
#default(listobs)
cts.listobs(vis=msfile, listfile=outdir+'listscan/listobs.txt', overwrite=True)
print('listobs saved in '+ outdir+'listscan/listobs.txt')

#Manually inspect bad antennas
try:
	os.system('mkdir ' + outdir+'ants')
except:
	None

for i in fluxcal:
    print(i)
    subprocess.run('casaplotms vis={}, field={},  spw=0:256, iteraxis=antenna, exprange=all, plotfile=out_CGCG032-017/ants/i.png, showgui=False, overwrite=True', shell=True, check=True)

