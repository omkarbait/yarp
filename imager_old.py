# This module contains several imaging recipes.

import subprocess
import casatasks as cts
    

def tcleaner(targetcalfile, params, threshold='1.0mJy', niter=1000, outimage=None, interactive=False):
    '''
    This tcleaner is specifically written for imaging during the self-calibration round. For a general purpose imaging, use the casa task tclean outside of yarrp. 
    '''

    imaging_params = params['imagecal']
    #outimage = imaging_params['outimage']
    target = params['general']['target']
    imsize = imaging_params['imsize']
    cell = imaging_params['cell']
    robust = imaging_params['robust'] 
    weighting = imaging_params['weighting']
    uvran = imaging_params['uvran']
    uvtaper = imaging_params['uvtaper']
    nterms = imaging_params['nterms']
    #niter = imaging_params['niter']
    #threshold = imaging_params['threshold']
    wprojplanes = imaging_params['wprojplanes']
    scales = imaging_params['scales']

    cts.tclean(targetcalfile, imagename=outimage, field=target, spw='0', imsize=imsize, cell=cell, robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper, 
       			specmode='mfs',	nterms=nterms, niter=niter, usemask='auto-multithresh', minbeamfrac=0.1, sidelobethreshold = 1.5,
			smallscalebias=0.6, threshold= threshold, aterm =True, pblimit=-1,
	        	deconvolver='mtmfs', gridder='wproject', wprojplanes=wprojplanes, scales=scales,wbawp=False,
			restoration = True, savemodel='modelcolumn', cyclefactor = 0.5, parallel=False,
       			interactive=interactive)

    return print('tcleaned the {}'.format(targetcalfile), 'file.')
