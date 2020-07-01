import parameters as prms
import flagger as flg
import calibrator as clb
import casatasks as cts
import subprocess
from  recipes import flagcal, imagecal
from imstats import stats


print('Doing cube image...')
# image the cube

params = prms.read('parameters.yaml')
outdir = params['general']['outdir']    
target = params['general']['target']
targetcalfile = params['general']['targetcalfile'] 
restfreq = '1.420405752GHz'
cont_sub_file = targetcalfile+'.contsub'
weighting = params['cube']['weighting']
robust = params['cube']['robust']
deconvolver = params['cube']['deconvolver']

#uvran_list = ['0.5~5klambda', '0.5~10klambda', '0.5~20klambda','0.5~40klambda'] # list of uvranges to image the cube
#uvtaper_list = ['4.5klambda', '6klambda', '12klambda', '30klambda']
#imsize_list = [256, 512, 540, 1024]
#cellsize_list = ['8arcsec', '4arcsec', '3arcsec', '1arcsec']
#threshold_list = ['0.44mJy', '1.0mJy', '1.0mJy', '1.0mJy']
 
#uvran_list = ['0.5~40klambda']
#uvtaper_list = ['30klambda']
#imsize_list = [1024]
#cellsize_list = ['1arcsec']
#threshold_list = ['1.0mJy']

uvran_list = ['0.5~5klambda', '0.5~20klambda']
uvtaper_list = ['4.5klambda', '12klambda']
imsize_list = [256, 540]
cellsize_list = ['8arcsec', '3arcsec']
threshold_list = ['1mJy', '1.0mJy']

vel_res1 = params['cube']['vel_res']
vel_res = str(vel_res1)+'km/s'
#vel_res = '-14km/s'
file_name = str(vel_res1)+'kmps'
for i in range(len(uvran_list)):
    print('Running the ', uvran_list[i], 'resolution cube...')
    cts.tclean(cont_sub_file, 
            imagename = outdir+target+'_cube_multiscale_'+str(file_name)+'/'+'uvran_'+str(uvran_list[i]),
            field = '0',
            spw = '0',
            specmode = 'cube',
            nchan = -1,
            width = vel_res,
            outframe = 'bary',
            veltype = 'optical',
            restfreq = restfreq,
            deconvolver= 'multiscale', #'hogbom',
            scales = [0, 5, 15],
            gridder = 'standard',
            uvrange = uvran_list[i],
            uvtaper = uvtaper_list[i],
            imsize = imsize_list[i],
            cell = cellsize_list[i],
            threshold= threshold_list[i],
            weighting = 'briggs',
            robust =  0,
            restoringbeam='common',
            interactive = False, 
            usemask='pb',
            pbmask=0.2,
            #usemask='auto-multithresh',
            #minbeamfrac=0.1, 
            #sidelobethreshold = 1.5,
            #smallscalebias=0.6,
            niter=100000
            )

