import parameters as prms
import flagger as flg
import calibrator as clb
import casatasks as cts

# apply the calibrations on the target
params = prms.read('parameters.yaml')
target = params['general']['target']
gaintables = params['calibration']['gaintables']


'''
print('Applying the calibration tables to the target...') 
msfile = '../blcal_test/CGCG032-017_cen1K_split.ms'
uvran = '0.5~100klambda'
phasecal = '0745+101'
cts.applycal(msfile, field=target, uvrange=uvran, gaintable=gaintables, gainfield=['','',phasecal], interp=['','','linear'], calwt=[False], parang=False)


# rflag the data
print('Mildly Rflagging the target at cutoff of 10 sigma...')
flg.rflagger(msfile, params, field=target, tcut=10, fcut=10, instance='postcal')
flg.extend(msfile, params, field=target, grow=80, instance='postcal')
# split the calibrated target data
out_cal_file = '../blcal_test/RGG5_yarrp_cal.ms'#params['general']['targetcalfile']

print('Splitting the target...')
cts.mstransform(msfile, field=target, spw='0', chanaverage=False, datacolumn='corrected', outputvis=out_cal_file)


print('Doing uvsub...')
target = params['general']['target']
targetcalfile = '../blcal_test/RGG5_cen1k_yarrp_cal.ms' #params['general']['targetcalfile']
avspcfile = targetcalfile[:-3]+'_avspc.ms' 
#nloops = params['imagecal']['nloops']
#ploops = params['imagecal']['ploops']
#aploops = params['imagecal']['aploops']

# apply self-cal table to the full chan resolution file
#selfcaltable = [outdir+'sc_p.gcal.'+str(nloops)+str(ploops), outdir+'sc_ap.gcal.'+str(nloops)+str(ploops)]
#cts.applycal(targetcalfile, gaintable=selfcaltable, field='', gainfield='', applymode='calonly', interp=['linear'], calwt=False, parang=False)

print('Rflagging the self-calibrated data')
linefreespw = params['uvsub']['linefreespw'] 
linespw = params['uvsub']['linespw']
flg.rflagger(targetcalfile, params, spw=linefreespw, field=target, tcut=6, fcut=6, instance='initial') # deep flag the line free channels
flg.rflagger(targetcalfile, params, spw=linespw, field=target, tcut=10, fcut=10, instance='initial') # Be  more conservative on the line channels
flg.extend(targetcalfile, params, field=target, grow=80, instance='initial')

# UVLIN the full chan resolution file
print('Doing uvcontsub...')

fitorder = params['uvsub']['fitorder']
#print(linefreespw)
cts.uvcontsub(targetcalfile, fitspw=linefreespw, fitorder=fitorder)
'''

# Doing a cube image
print('Doing a cube image on a blcaled file...')
outdir = '../blcal_test/'
targetcalfile = '../blcal_test/RGG5_cen1k_yarrp_cal.ms' #params['general']['targetcalfile']
target = params['general']['target']
cont_sub_file = targetcalfile+'.contsub'
restfreq = '1.420405752GHz'

uvran_list = ['0.5~5klambda', '0.5~20klambda']
uvtaper_list = ['4.5klambda', '12klambda']
imsize_list = [256, 540]
cellsize_list = ['8arcsec', '3arcsec']
threshold_list = ['1mJy', '1.0mJy']

'''
#uvran_list = ['0.5~40klambda']
#uvtaper_list = ['30klambda']
#imsize_list = [1024]
#cellsize_list = ['1arcsec']
#threshold_list = ['1.0mJy']

#uvran_list = ['1~30klambda']
#uvtaper_list = ['25klambda']
#imsize_list = [1024]
#cellsize_list = ['1arcsec']
#threshold_list = ['1.0mJy']
'''

vel_res1 = params['cube']['vel_res']
vel_res = str(vel_res1)+'km/s'
#vel_res = '-14km/s'
file_name = str(vel_res1)+'kmps'
for i in range(len(uvran_list)):
    print('Running the ', uvran_list[i], 'resolution cube...')
    cts.tclean(cont_sub_file, 
            #imagename = outdir+target+'_cube_multiscale_'+str(file_name)+'/'+'uvran_'+str(uvran_list[i]),
            imagename = outdir+target+'_cube_'+str(file_name)+'/'+'uvran_'+str(uvran_list[i]),
            field = '0',
            spw = '0',
            specmode = 'cube',
            nchan = -1,
            width = vel_res,
            outframe = 'bary',
            veltype = 'optical',
            restfreq = restfreq,
            deconvolver= 'hogbom', # 'multiscale',
            #scales = [0, 5, 15],
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
            pbmask=0.05,
            #usemask='auto-multithresh',
            #minbeamfrac=0.1, 
            #sidelobethreshold = 1.5,
            #smallscalebias=0.6,
            niter=100000
            )


