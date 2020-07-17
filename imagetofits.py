import subprocess
import casatasks as cts
import parameters as prms

#cts.exportfits(imagename='/mnt/work/work/HI_DATA/out_RGG5/RGG5_cube_14kmps/uvran_0.5~20klambda.image', fitsimage="../out_RGG5/RGG5_finalcube_20lkambda.fits", dropstokes = True, velocity = True)

cts.exportfits(imagename='/Data/omkar/HI_DATA/quenched_hi/out_AGC722572/AGC722572_cube_14kmps/uvran_0.5~5klambda.image', fitsimage="/Data/omkar/HI_DATA/quenched_hi/out_AGC722572/AGC722572_cube_14kmps/AGC722572_finalcube_5lkambda.fits", dropstokes = True, velocity = True)
#cts.exportfits(imagename='/mnt/work/work/HI_DATA/blcal_test/RGG5_cube_multiscale_14kmps/uvran_1~30klambda.image', fitsimage="../blcal_test/RGG5_finalcube_msclean_30lkambda.fits", dropstokes = True, velocity = True)

