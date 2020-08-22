import os
import parameters
import casatasks as cts

#params = parameters.read('parameters.yaml')
#general_params = params['general'] # loading general params
#msfile = general_params['msfile']

# import UV data
fitsfile = '/Data/omkar/HI_DATA/quenched_hi/AGC203001/AGC203001_SCAN2.FITS'
cts.importgmrt(fitsfile=fitsfile, vis='/Data/omkar/HI_DATA/quenched_hi/AGC203001/AGC203001_scan2.ms')


# Select only the central 1K channels

#msfile = '/Data/omkar/HI_DATA/quenched_hi/AGC190633/09aug/AGC203001/AGC203001_scan1.ms'

#tot_chans = 8192
#cen_chan = 8192/2 + 1
#print('Splitting the central 1K channels ...')
#cts.split(vis=msfile, outputvis=msfile[0:-3]+'_cen1K.ms', spw='0:4513~5347', datacolumn='data')
print('Done')
