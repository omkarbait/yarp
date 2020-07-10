import os
import parameters
import casatasks as cts

#params = parameters.read('parameters.yaml')
#general_params = params['general'] # loading general params
#msfile = general_params['msfile']

# import UV data
#fitsfile = '../36_068_10AUG19/AGC722572.FITS'
#cts.importgmrt(fitsfile=fitsfile, vis='../36_068_10AUG19/agc722572.ms')

# Select only the central 1K channels
msfile = '../36_068_10AUG19/agc722572.ms'

#tot_chans = 8192
#cen_chan = 8192/2 + 1
print('Splitting the central 1K channels ...')
cts.split(vis=msfile, outputvis=msfile[0:-3]+'_10Mhz.ms', spw='0:4506~4915', datacolumn='all')
print('Done')
