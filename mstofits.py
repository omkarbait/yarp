import subprocess
import casatasks as cts
import parameters as prms

msfile = '/Data/omkar/HI_DATA/BB10_HI/04FEB_GWB_cen1K.ms'

fitsfile = '/Data/omkar/HI_DATA/BB10_HI/BB10_HI.FITS'

cts.exportuvfits(vis=msfile, fitsfile=fitsfile, datacolumn="data", overwrite=False)

