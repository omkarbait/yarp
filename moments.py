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
uvran = '0.5~40klambda'
imagename = outdir+target+'_cube_'+str(file_name)+'/'+'uvran_'+str(uvran)+'.image'

#imagename = outdir+'RGG5_cube_7kmps_hogbom/uvran_0.5~40klambda.image' 

smooth_name = imagename+'_hanningsmooth.im'
#outname = imagename
# For 5klambda 20kmps cube chans='66~72'
# For 20 klambda 14 kmps cube chans='87~105', mom1 = '85~103'


cts.immoments(axis='spec', imagename=smooth_name, moments=0, region='../regions/RGG5_region.crtf', includepix=[2e-3,170] , chans='60~74', outfile=smooth_name+'.mom0')
#cts.immoments(axis='spec', imagename=smooth_name, moments=0, region='../regions/mom_region.crtf', chans='40~54', outfile=smooth_name+'_rms.mom0')

#cts.immoments(axis='spec', imagename=smooth_name, moments=1, region='../regions/mom_region.crtf', includepix=[2.5e-3,170] , chans='61~73', outfile=smooth_name+'.mom1')

