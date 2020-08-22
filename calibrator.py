# This module contains several flagging recipes.
import subprocess
import casatasks as cts


def delaycal(msfile, params, field=None):

    refant = params['flagging']['refant']
    caltable = params['calibration']['delaytable']
    gaintables = params['calibration']['gaintables']
    uvran = params['general']['uvran']

    cts.gaincal(msfile, field=field, solint='60s',  spw='0', uvrange=uvran, refant=refant,
                caltable=caltable, gaintype='K', solnorm=True, gaintable=gaintables, parang=True)
    return print('Delay calibration done')


def bpasscal(msfile, params, field=None):

    refant = params['flagging']['refant']
    bpassgaintable = params['calibration']['bpassgaintable']
    bpasstable = params['calibration']['bpasstable']
    gaintables = params['calibration']['gaintables']
    uvran = params['general']['uvran']
    ch0_spw = params['calibration']['ch0_spw']
    # Initial gain calibration
    cts.gaincal(msfile, caltable=bpassgaintable, field=field, uvrange=uvran, spw='0', solint='int', solmode='R', refant=refant,
                minsnr=2.0, gaintype='G', calmode='ap', gaintable=gaintables, interp=['linear, linear', ], append=True, parang=False)
    gaintables.append(bpassgaintable)
    print(gaintables, 'before bpass')
    # bpass calibration
    cts.bandpass(msfile, caltable=bpasstable, spw='0', field=field, uvrange=uvran,  solint='inf', refant=refant, solnorm=True,
                 minsnr=2.0, append=True, fillgaps=8, parang=False, gaintable=gaintables, interp=['linear,linear', 'linear,linear'])
    #cts.bandpass(msfile, caltable=bpasstable, spw ='0', field=field, solint='inf', refant=refant, solnorm = True, minsnr=2.0, fillgaps=8, bandtype='BPOLY', degamp=5, degphase=7, parang = True, gaintable=gaintables, interp=['nearest,nearestflag','nearest,nearestflag'])

    # Removing and also deleting the on-the fly gaincal table used for bandpass
    subprocess.run('rm -r {}'.format(bpassgaintable), shell=True, check=True)
    gaintables.remove(bpassgaintable)

    return print('Bandpass calibration done')


def bpasscal2(msfile, params, field=None):

    refant = params['flagging']['refant']
    bpassgaintable = params['calibration']['bpassgaintable']
    bpasstable = params['calibration']['bpasstable']
    gaintables = params['calibration']['gaintables']
    uvran = params['general']['uvran']
    ch0_spw = params['calibration']['ch0_spw']
    ini_fgloops = params['calibration']['ini_nloops']
    fluxcal = params['general']['fluxcal']
    # Initial gain calibration

    # for i in range(ini_fgloops):
    print('Running the initial gaincal pre-bandpass ...')

    cts.gaincal(msfile, caltable=bpassgaintable, field=field, uvrange=uvran, spw=ch0_spw, solint='120s', solmode='R', refant=refant,
                minsnr=2.0, gaintype='G', calmode='p', gaintable=gaintables, interp=['linear, linear', ], append=True, parang=False)
    ''' 
        for j in fluxcal:
            #print('Applying the calibration table to ', i)
            cts.applycal(msfile, field=j, spw=ch0_spw, gaintable=bpassgaintable, gainfield=[
                         '', '', j], uvrange=uvran, interp=['', '', 'linear'], calwt=[False], parang=False)

            #cts.flagdata(msfile, mode='tfcrop', datacolumn='corrected', field=j, ntime='scan', spw=ch0_spw,
            #                    timecutoff=6, freqcutoff=6, timefit='poly',freqfit='line',flagdimension='time',
            #                    extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
            #                    action='apply', flagbackup=True,overwrite=True, writeflags=True)
            #cts.flagdata(msfile, params, field=j, tcut=6, fcut=6, instance='postcal')
            #flg.extend(msfile, params, field=j, grow=80, instance='postcal')

        cts.clearcal(msfile)  # Removes the corrected datacolumn
        if i == (ini_fgloops - 1):
            print('Single channel flagcal loops ended.')
            break
        else:
            subprocess.run('rm -r {}'.format(bpassgaintable), shell=True, check=True)
        '''
    gaintables.append(bpassgaintable)
    print(gaintables, 'before bpass')
    # bpass calibration
    cts.bandpass(msfile, caltable=bpasstable, spw='0', field=field, uvrange=uvran,  solint='inf', refant=refant, solnorm=True,
                 minsnr=2.0, append=True, fillgaps=8, parang=False, gaintable=gaintables, interp=['linear,linear', 'linear,linear'])
    #cts.bandpass(msfile, caltable=bpasstable, spw ='0', field=field, solint='inf', refant=refant, solnorm = True, minsnr=2.0, fillgaps=8, bandtype='BPOLY', degamp=5, degphase=7, parang = True, gaintable=gaintables, interp=['nearest,nearestflag','nearest,nearestflag'])

    # Removing and also deleting the on-the fly gaincal table used for bandpass
    subprocess.run('rm -r {}'.format(bpassgaintable), shell=True, check=True)
    gaintables.remove(bpassgaintable)

    return print('Bandpass calibration done')
# The main amplitude and phase calibrator


def apcal(msfile, params, field=None):
    refant = params['flagging']['refant']
    gaintables = params['calibration']['gaintables']
    apgaintable = params['calibration']['apgaintable']
    uvran = params['general']['uvran']
    spw = params['general']['spw']

    print(gaintables, 'before ampcal')
    cts.gaincal(vis=msfile, caltable=apgaintable, spw=spw, append=True, field=field, uvrange=uvran, solint='60s', refant=refant,
                minsnr=3.0, gaintype='G', calmode='ap', solmode='R', gaintable=gaintables, interp=['linear, linear', 'linear, linear'], parang=True)

    return print('Amplitude and phase calibration done for ', field)


def selfcal(msfile, params, mode='p', in_gaintable=[], out_gaintable='sc_p.test.gcal', solint='8min'):
    refant = params['flagging']['refant']
    #print(gaintables, 'before selfcal')
    if mode == 'p':
        minsnr = 3.0
        solnorm = False
    elif mode == 'ap':
        minsnr = 3.0
        solnorm = True

    cts.gaincal(msfile, caltable=out_gaintable, append=False, field='0', spw='0', uvrange='', solint=solint, refant=refant, minsnr=minsnr,
                gaintype='G', solnorm=solnorm, calmode=mode, solmode='R', gaintable=in_gaintable, interp=['nearestobsid, nearestobsid'], parang=False)
    return None
