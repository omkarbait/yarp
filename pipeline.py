import parameters as prms
import flagger as flg
import calibrator as clb
import casatasks as cts
import subprocess
from  recipes import flagcal, flagcal_bl, imagecal, imagecal2

def pipeline(msfile, params, doinitial_flagging=True, doflagcal=True, doimagecal=True, douvsub=True, docubeimage=False):
    '''
    This function takes combines several recipes to construct a pipeline. In particular here it follows a simple procedure. 

    initial flagging --> setjy+delay calibration --> amplitude calibration + flagging loops on calibrators --> bandpass calibration + flagging loops --> imaging+selfcal loops --> final image --> UVSUB+CVEL --> Cube image with source finder. 
    ''' 
    with open('yarrp_art.txt', 'r') as f:
        for line in f:
            print(line.rstrip())   
    print('Running the yarrp pipeline on {}'.format(msfile))    
    if doinitial_flagging:
        flg.badantflag(msfile, params)
        cts.flagdata(msfile, mode='quack', field='', spw='0', antenna='', correlation='', timerange='', quackinterval=10, quackmode='beg', action='apply', savepars=True, cmdreason='quackbeg')
        cts.flagdata(msfile, mode='quack', field='', spw='0', antenna='', correlation='', timerange='', quackinterval=10, quackmode='endb', action='apply', savepars=True, cmdreason='quackendb')
        flg.tfcropper(msfile, params, field='', tcut=6, fcut=6, instance='initial')
        cts.flagdata(msfile, mode='manual', uvrange='>100klambda') # Flag very long baselines as that can affect the calibration  
        flg.extend(msfile, params, instance='initial')
        #flg.aoflagger(msfile, params)
    else:
        print('No initial flagging this time.')
        
    
    # Flagcal begins

    if doflagcal:
        print('Running the flagcal script...')
        flagcal_bl(msfile, params, niters=5, flagger='default', interactive=False)
    else:
        print('No flagcal this time.')

    if doimagecal:
        print('Doing image and self-calibration...')
        target = params['general']['target']
        targetcalfile = params['general']['targetcalfile']
        avspcfile = targetcalfile[:-3]+'_avspc.ms' 
        
        print('Flagging all data above uvran 100klambda ...')
        cts.flagdata(targetcalfile, mode='manual', uvrange='>100klambda') 
        print('Averaging the channels to 1 MHz...')
        chanbin = params['imagecal']['chanbin']
        cts.mstransform(targetcalfile, field=target, spw='0', chanaverage=True, chanbin=chanbin, datacolumn='data', outputvis=avspcfile)
        print('Rflagging the channel averaged file...')
        flg.rflagger(avspcfile, params, field=target, tcut=10, fcut=10, instance='initial')
        flag_spw = params['imagecal']['spec_line_spw']
        cts.flagdata(avspcfile, mode='manual', spw=flag_spw)
        print('Doing imaging and self-calibration...')
        
        nloops = params['imagecal']['nloops']
        ploops = params['imagecal']['ploops']
        aploops = params['imagecal']['aploops']
        print('Running {} cycles of self-cal with {} ploops and {} aploops in each cycle...'.format(str(nloops), str(ploops), str(aploops)))
        final_image, selfcaltable = imagecal(avspcfile, params, nloops=nloops, ploops=ploops, aploops=aploops, flagger='default', interactive=False)
        print('Final self-cal table is', selfcaltable) 
    
    else:
        print('No imaging and self-calibration this time.')
    
    if douvsub:
        print('Doing uvsub...')
        target = params['general']['target']
        targetcalfile = params['general']['targetcalfile']
        avspcfile = targetcalfile[:-3]+'_avspc.ms' 
        nloops = params['imagecal']['nloops']
        ploops = params['imagecal']['ploops']
        aploops = params['imagecal']['aploops']

        # apply self-cal table to the full chan resolution file
        selfcaltable = [outdir+'sc_p.gcal.'+str(nloops)+str(ploops), outdir+'sc_ap.gcal.'+str(nloops)+str(ploops)]
        cts.applycal(targetcalfile, gaintable=selfcaltable, field='', gainfield='', applymode='calonly', interp=['linear'], calwt=False, parang=False)
    
        print('Rflagging the self-calibrated data')
        linefreespw = params['uvsub']['linefreespw'] 
        linespw = params['uvsub']['linespw']
        flg.rflagger(targetcalfile, params, spw=linefreespw, field=target, tcut=6, fcut=6, instance='postcal') # deep flag the line free channels
        flg.rflagger(targetcalfile, params, spw=linespw, field=target, tcut=10, fcut=10, instance='postcal') # Be  more conservative on the line channels
        flg.extend(targetcalfile, params, field=target, grow=80, instance='postcal')
    
        # UVLIN the full chan resolution file
        print('Doing uvcontsub...')

        fitorder = params['uvsub']['fitorder']
        #print(linefreespw)
        cts.uvcontsub(targetcalfile, fitspw=linefreespw, fitorder=fitorder)

    else:
        print('No uvsub this time.')


    if docubeimage:
        print('Doing cube image...')
        # image the cube
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
         
        uvran_list = ['0.5~5klambda']
        uvtaper_list = ['4.5klambda']
        imsize_list = [256]
        cellsize_list = ['8arcsec']
        threshold_list = ['1mJy']
        
        vel_res1 = params['cube']['vel_res']
        vel_res = str(vel_res1)+'km/s'
        #vel_res = '-14km/s'
        file_name = str(vel_res1)+'kmps'
        for i in range(len(uvran_list)):
            cts.tclean(cont_sub_file, 
                    imagename = outdir+target+'_cube_'+str(file_name)+'/'+'uvran_'+str(uvran_list[i]),
                    field = '0',
                    spw = '0',
                    specmode = 'cube',
                    nchan = -1,
                    width = vel_res,
                    outframe = 'bary',
                    veltype = 'optical',
                    restfreq = restfreq,
                    deconvolver= 'hogbom',
                    gridder = 'standard',
                    uvrange = uvran_list[i],
                    uvtaper = uvtaper_list[i],
                    imsize = imsize_list[i],
                    cell = cellsize_list[i],
                    threshold= threshold_list[i],
                    weighting = 'natural',#weighting,
                    robust =  2, #robust,
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
    else:
        print('No cube image this time.')
    
    outdir = general_params['outdir']
    subprocess.run('cp {} {}'.format('parameters.yaml', outdir), shell=True, check=True)
    
    targetcalfile = params['general']['targetcalfile'] 
    cont_sub_file = targetcalfile+'.contsub'
    subprocess.run('cp -r {} {}'.format(cont_sub_file, outdir), shell=True, check=True)
    

    return print('yarrp pipeline ended.')

    
if __name__ == "__main__":
    params = prms.read('parameters.yaml')
    general_params = params['general'] # loading general params
    msfile = general_params['msfile']
    outdir = general_params['outdir']
    fluxcal= general_params['fluxcal']
    pipeline(msfile, params, doinitial_flagging=False, doflagcal=False, doimagecal=False, douvsub=True, docubeimage=False)


