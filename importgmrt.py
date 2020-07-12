import os
import parameters
import casatasks as cts

#params = parameters.read('parameters.yaml')
#general_params = params['general'] # loading general params
#msfile = general_params['msfile']

# import UV data
#fitsfile = '../quenched_hi/AGC722572.FITS'
#cts.importgmrt(fitsfile=fitsfile, vis='../quenched_hi/agc722572.ms')


# Select only the central 1K channels

msfile = '../quenched_hi/agc722572.ms'

#tot_chans = 8192
#cen_chan = 8192/2 + 1
print('Splitting the central 1K channels ...')
cts.split(vis=msfile, outputvis=msfile[0:-3]+'_cen1K.ms', spw='0:4513~5347', datacolumn='data')
print('Done')
