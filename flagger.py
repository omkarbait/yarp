# This module contains several flagging recipes.

import subprocess
import casatasks as cts

def badantflag(msfile, params):
	general_params = params['general'] # loading general params
	badants = params['flagging']['badants']
	ants = ','.join(badants)
	cts.flagdata(msfile, mode='manual', antenna=ants, action='apply')
	return print('Flagged non-working antennas:', ants)


def aoflagger(msfile, params):
    subprocess.run('aoflagger -indirect-read {}'.format(msfile), shell=True, check=True)
    return None

def clipper(msfile, params, field=None, cliplevel=100, instance='initial'):
    if instance == 'initial':
        datacol = 'data'
        sources = ''
 
    elif instance == 'postcal':
        datacol = 'corrected'
        sources = field
    else:
        print('Please provide a relevant instance.[initial/postcal] ')
        
    spw = params['general']['spw']     
    cts.flagdata(msfile , mode='clip', spw=spw, field=sources, clipminmax=cliplevel, datacolumn=datacol, clipoutside=True, clipzeros=True, extendpols=False, action='apply',flagbackup=True, savepars=False, overwrite=True, writeflags=True)
    
    return print('Data flagged with clipper at ', cliplevel)

def tfcropper(msfile, params, field=None, tcut=10.0, fcut=10.0, instance='initial'):
    spw = params['general']['spw']     
    
    if instance == 'initial':
        cts.flagdata(msfile, mode='tfcrop', datacolumn='data', field='', ntime='scan', spw=spw,
                            timecutoff=tcut, freqcutoff=fcut, timefit='poly',freqfit='poly',flagdimension='timefreq',
                            extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
                            action='apply', flagbackup=True,overwrite=True, writeflags=True)

    elif instance == 'postcal':

        cts.flagdata(msfile, mode='tfcrop', datacolumn='corrected', field=field, ntime='scan', spw=spw,
                            timecutoff=tcut, freqcutoff=fcut, timefit='poly',freqfit='line',flagdimension='timefreq',
                            extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
                            action='apply', flagbackup=True,overwrite=True, writeflags=True)
    return print('Data flagged with tfcrop.')

def rflagger(msfile, params, spw='0', field=None, tcut=10.0, fcut=10.0, instance='initial'):

    #spw = params['general']['spw']     
    
    if instance == 'initial':
        cts.flagdata(msfile, mode='rflag', datacolumn='data', field=field, ntime='scan', spw=spw, timecutoff=tcut, 
		        freqcutoff=fcut, timefit='poly',freqfit='poly',flagdimension='timefreq', extendflags=False,
		        timedevscale=5.0,freqdevscale=5.0,extendpols=False, growaround=False,
		        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
 
    elif instance == 'postcal':
        cts.flagdata(msfile, mode='rflag', datacolumn='corrected', field=field, ntime='scan', spw=spw, timecutoff=tcut, 
		        freqcutoff=fcut, timefit='poly',freqfit='line',flagdimension='freqtime', extendflags=False,
		        timedevscale=5.0,freqdevscale=5.0,extendpols=False, growaround=False,
		        flagneartime=False,flagnearfreq=False,action='apply',flagbackup=True,overwrite=True, writeflags=True)
    
        
        
    return print('Data flagged with rflag.')


def extend(msfile, params, field=None, grow=90, instance='initial'):
    
    if instance == 'initial':
        datacol = 'data'
        sources = ''
    elif instance == 'postcal':
        datacol = 'corrected'
        sources = field

    else:
        print('Please provide a relevant instance.[initial/postcal] ')
    
    cts.flagdata(msfile, mode="extend", field=sources, datacolumn=datacol, clipzeros=True, ntime="scan", extendflags=False, extendpols=True, growtime=grow, growfreq=grow, growaround=False, flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True, overwrite=True, writeflags=True)

    return print('Flags extended with a grow of', grow)

