import os
import parameters
import casatasks as cts

params = parameters.read('parameters.yaml')
general_params = params['general'] # loading general params
msfile = general_params['msfile']

# import UV data
fitsfile = '../CGCG032-017_cen1K_split_flagcal.FITS'
cts.importgmrt(fitsfile=fitsfile, vis='../CGCG032-017_cen1K_split_flagcal.MS')


'''
# Select only the central 1K channels
tot_chans = 8192
cen_chan = 8192/2 + 1
print('Splitting the central 1K channels ...')
cts.split(vis=msfile, outputvis=msfile[0:-3]+'_cen1K_split.ms', spw='0:3596~4596', datacolumn='all')
print('Done')
'''
