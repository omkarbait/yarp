import subprocess
import casatasks as cts
import parameters as prms


''' 
Run smooth.py if you want a smoothed cube before making moment maps
'''
params = prms.read('parameters.yaml')
outdir = params['general']['outdir']    
target = params['general']['target']
vel_res1 = params['cube']['vel_res']
vel_res = str(vel_res1)+'km/s'
#vel_res = '-14km/s'
file_name = str(vel_res1)+'kmps'
uvran = '0.5~5klambda'
imagename = outdir+target+'_cube_'+str(file_name)+'/'+'uvran_'+str(uvran)+'.image'

#imagename = outdir+'RGG5_cube_7kmps_hogbom/uvran_0.5~40klambda.image' 

imagename = '/Data/omkar/HI_DATA/quenched_hi/out_AGC722572/AGC722572_cube_multiscale_7kmps/uvran_0.5~5klambda.image'
smooth_name = imagename+'_hanningsmooth.im'
print(smooth_name)
#outname = imagename
# For 5klambda 20kmps cube chans='66~72'
# For 20 klambda 14 kmps cube chans='87~105', mom1 = '85~103'

#region = '/Data/omkar/HI_DATA/quenched_hi/AGC722572/out_AGC722572/regions/AGC722572_mom_region.crtf'
region = 'box [[10:49:56.32923, +025.58.20.6945], [10:49:03.81253, +026.05.47.4442]]'
cts.immoments(axis='spec', imagename=smooth_name, moments=0, region=region, includepix=[1e-3,170] , chans='90~98', outfile=smooth_name+'.mom0')
#cts.immoments(axis='spec', imagename=smooth_name, moments=0, region='../regions/mom_region.crtf', chans='40~54', outfile=smooth_name+'_rms.mom0')

#cts.immoments(axis='spec', imagename=smooth_name, moments=1, region=region, includepix=[2e-3,170] , chans='90~98', outfile=smooth_name+'.mom1')

