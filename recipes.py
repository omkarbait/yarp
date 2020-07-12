import numpy as np
import parameters as prms
import flagger as flg
import calibrator as clb
import imager as imgr
import casatasks as cts
import subprocess
from imstats import stats
from astropy.table import Table
import matplotlib.pyplot as plt


params = prms.read('parameters.yaml')

general_params = params['general']  # loading general params
msfile = general_params['msfile']
outdir = general_params['outdir']
fluxcal = general_params['fluxcal']
spw = params['general']['spw']


def flagcal(msfile, params, niters=1, flagger='default', interactive=False):
    '''
    This function takes an initially flagged msfile and goes through the flagging and calibration loops. It does delaycal, bandpass and a amplitude and phase cals. It then flags the data and then continues to the calibration cycle. The loops continue till niters end or in the interactive mode when the user is satisfied. The calibration in then applied to the source and it is mildly flagged using Rflag and splitted in a seperate msfile.
    '''

    fcals = ','.join(fluxcal)  # joining the fluxcals in a casa readable format

    # Main flagcal loops begin

    flagcal_fin = 'n'  # a flag to denote finished flagging
    loop = 1  # Keeping a track of number of iterations
    while flagcal_fin == 'n':
        # Beginning with an empty gaintable list, which will be succesively appended after every calibration.
        gaintables = []
        params['calibration'].update({'gaintables': gaintables})
        # writes the gaintables column in the parameters file.
        prms.write(params, 'parameters.yaml')
        cts.setjy(msfile, field=fcals, scalebychan=True,
                  standard='Perley-Butler 2017', listmodels=False, usescratch=False)

        clb.delaycal(msfile, params, field=fcals)
        # append the caltable and save the params file
        params['calibration']['gaintables'].append(
            params['calibration']['delaytable'])
        prms.write(params, 'parameters.yaml')
        if interactive:
            caltable = params['calibration']['delaytable']
            subprocess.run('casaplotms vis={} field={}'.format(
                caltable, fcals), shell=True, check=True)
            antflag = input(
                "Do you want to flag any antenna(s) ? [y/n] \n If yes, append the bad antennas in the params file now.")
            if antflag == 'y':
                flg.badantflag(msfile, params)
            else:
                print('No flagging after delaycal.')

        else:
            None

        # Using fluxcals for bandpass calibration
        clb.bpasscal(msfile, params, field=fcals)
        params['calibration']['gaintables'].append(
            params['calibration']['bpasstable'])
        prms.write(params, 'parameters.yaml')

        # Joining all the calibrators and doing amplitutde and phase calibration
        phasecal = params['general']['phasecal']
        print('Phasecal is ', phasecal)
        allcals = fluxcal + [phasecal]

        # for i in allcals:
        #    clb.apcal(msfile, params, field=i)

        allcals2 = ','.join(allcals)
        clb.apcal(msfile, params, field=allcals2)

        # Adding the amplitude and phase calibration tables in gaintables
        params['calibration']['gaintables'].append(
            params['calibration']['apgaintable'])
        prms.write(params, 'parameters.yaml')

        uvran = params['general']['uvran']

        # GETJY
        print('Setting the absolute fluxscale for ', phasecal)
        fluxtbl = params['calibration']['fluxscaletable']

        phasecal_flux = cts.fluxscale(msfile, caltable=params['calibration']['apgaintable'],
                                      fluxtable=fluxtbl, reference=fcals, transfer=phasecal, incremental=False, append=False)
        print('The flux density of {}'.format(phasecal)+'is',
              phasecal_flux['1']['0']['fluxd'][0], '+/-', phasecal_flux['1']['0']['fluxdErr'][0])
        # Replace the apgaintable with fluxscale table
        params['calibration']['gaintables'].remove(
            params['calibration']['apgaintable'])
        params['calibration']['gaintables'].append(fluxtbl)
        prms.write(params, 'parameters.yaml')
        subprocess.run(
            'rm -r {}'.format(params['calibration']['apgaintable']), shell=True, check=True)

        # Applying the calibrations on flux cal
        gaintables = params['calibration']['gaintables']
        for i in fluxcal:
            print('Applying the calibration table to ', i)

            cts.applycal(msfile, field=i, spw=spw, gaintable=gaintables, gainfield=[
                         '', '', i], uvrange=uvran, interp=['', '', 'linear'], calwt=[False], parang=False)

        # Apply the calibration on phase cal
        cts.applycal(msfile, field=phasecal, uvrange=uvran, gaintable=gaintables, gainfield=[
                     '', '', phasecal], interp=['', '', 'linear'], calwt=[False], parang=False)

        # Flagging after calibration

        def clip_est(fluxscale, nsigma, loop, beta):
            return [fluxscale - nsigma/loop**beta, fluxscale + nsigma/loop**beta]

        # fluxscale_list = [15, 22.5, 3.3]
        # uplims_list = [20, 20, 20]
        # beta=[0.5, 0.6, 0.6]
        # tcut_list = [6, 6, 10]
        # fcut_list = [6, 6, 10]
        pcal_flux = np.float(phasecal_flux['1']['0']['fluxd'][0])
        fluxscale_list = params['general']['fluxscale_list']
        fluxscale_list.append(pcal_flux)
        uplims_list = params['flagging']['uplims_list']
        beta = params['flagging']['beta']
        tcut_list = params['flagging']['tcut_list']
        fcut_list = params['flagging']['fcut_list']

        if flagger == 'default':
            for j, i in enumerate(allcals):
                flg.clipper(msfile, params, field=i, cliplevel=clip_est(
                    fluxscale_list[j], uplims_list[j], loop, beta[j]), instance='postcal')
                flg.tfcropper(
                    msfile, params, field=i, tcut=tcut_list[j], fcut=fcut_list[j], instance='postcal')
                flg.extend(msfile, params, field=i,
                           grow=80, instance='postcal')
                print('Flagged', i, 'postcalibration.')
            # Flag the phasecal using rflag
            flg.rflagger(msfile, params, field=phasecal,
                         tcut=10, fcut=10, instance='postcal')
            flg.extend(msfile, params, field=phasecal,
                       grow=80, instance='postcal')

        else:
            print('No flagging.')

        if interactive:
            subprocess.run('casaplotms vis={} field={}'.format(
                msfile, fluxcal[0]), shell=True, check=True)
            flagcal_fin = input(
                'Are you satisfied with the calibration?[y/n] ')
            # Remove the old cal tables before continuing
            for i in gaintables:
                subprocess.run('rm -r {}'.format(i), shell=True, check=True)

            continue
        else:
            print('Flagcal running in automode.')
            niters = niters - 1
            loop = loop + 1

            if niters < 1:
                print('Flagcal loops finished.')
                break
            else:
                # Remove all the old cal tables before continuing.
                print('Clearing the corrected column and fluxcal model...')
                cts.clearcal(msfile)  # Removes the corrected datacolumn
                cts.delmod(msfile)  # Removes the setjy model

                print('Clearing all the gaintables...')
                for i in gaintables:
                    print(i)
                    subprocess.run('rm -r {}'.format(i),
                                   shell=True, check=True)

                continue

    else:
        print('Calibration of flux and phase calibrators done.')

    # apply the calibrations on the target
    target = params['general']['target']
    print('Applying the calibration tables to the target...')
    gaintables = params['calibration']['gaintables']
    cts.applycal(msfile, field=target, uvrange=uvran, gaintable=gaintables, gainfield=[
                 '', '', phasecal], interp=['', '', 'linear'], calwt=[False], parang=False)

    # rflag the data
    print('Mildly Rflagging the target at cutoff of 10 sigma...')
    flg.rflagger(msfile, params, field=target,
                 tcut=10, fcut=10, instance='postcal')
    flg.extend(msfile, params, field=target, grow=80, instance='postcal')

    # split the calibrated target data
    out_cal_file = params['general']['targetcalfile']

    print('Splitting the target...')
    cts.mstransform(msfile, field=target, spw=spw, chanaverage=False,
                    datacolumn='corrected', outputvis=out_cal_file)

    return print('Flagcal script done.')


def flagcal2(msfile, params, niters=1, flagger='default', interactive=False):
    '''
    This function takes an initially flagged msfile and goes through the flagging and calibration loops. It does delaycal, bandpass and a amplitude and phase cals. It then flags the data and then continues to the calibration cycle. The loops continue till niters end or in the interactive mode when the user is satisfied. The calibration in then applied to the source and it is mildly flagged using Rflag and splitted in a seperate msfile.
    Here instead of using all the channels before bpass, a user defined single channel is used to go the gaincal before bpass. For this the bandpass2 function is used. This is the only change introduced in flagcal2 compared to the previous flagcal. 
    '''

    fcals = ','.join(fluxcal)  # joining the fluxcals in a casa readable format

    # Main flagcal loops begin

    flagcal_fin = 'n'  # a flag to denote finished flagging
    loop = 1  # Keeping a track of number of iterations
    while flagcal_fin == 'n':
        # Beginning with an empty gaintable list, which will be succesively appended after every calibration.
        gaintables = []
        params['calibration'].update({'gaintables': gaintables})
        # writes the gaintables column in the parameters file.
        prms.write(params, 'parameters.yaml')
        cts.setjy(msfile, field=fcals, scalebychan=True,
                  standard='Perley-Butler 2017', listmodels=False, usescratch=False)

        clb.delaycal(msfile, params, field=fcals)
        # append the caltable and save the params file
        params['calibration']['gaintables'].append(
            params['calibration']['delaytable'])
        prms.write(params, 'parameters.yaml')
        if interactive:
            caltable = params['calibration']['delaytable']
            subprocess.run('casaplotms vis={} field={}'.format(
                caltable, fcals), shell=True, check=True)
            antflag = input(
                "Do you want to flag any antenna(s) ? [y/n] \n If yes, append the bad antennas in the params file now.")
            if antflag == 'y':
                flg.badantflag(msfile, params)
            else:
                print('No flagging after delaycal.')

        else:
            None

        # Using fluxcals for bandpass calibration
        clb.bpasscal2(msfile, params, field=fcals)
        params['calibration']['gaintables'].append(
            params['calibration']['bpasstable'])
        prms.write(params, 'parameters.yaml')

        # Joining all the calibrators and doing amplitutde and phase calibration
        phasecal = params['general']['phasecal']
        print('Phasecal is ', phasecal)
        allcals = fluxcal + [phasecal]

        # for i in allcals:
        #    clb.apcal(msfile, params, field=i)

        allcals2 = ','.join(allcals)
        clb.apcal(msfile, params, field=allcals2)

        # Adding the amplitude and phase calibration tables in gaintables
        params['calibration']['gaintables'].append(
            params['calibration']['apgaintable'])
        prms.write(params, 'parameters.yaml')

        uvran = params['general']['uvran']

        # GETJY
        print('Setting the absolute fluxscale for ', phasecal)
        fluxtbl = params['calibration']['fluxscaletable']

        phasecal_flux = cts.fluxscale(msfile, caltable=params['calibration']['apgaintable'],
                                      fluxtable=fluxtbl, reference=fcals, transfer=phasecal, incremental=False, append=False)
        print('The flux density of {}'.format(phasecal)+'is',
              phasecal_flux['1']['0']['fluxd'][0], '+/-', phasecal_flux['1']['0']['fluxdErr'][0])
        # Replace the apgaintable with fluxscale table
        params['calibration']['gaintables'].remove(
            params['calibration']['apgaintable'])
        params['calibration']['gaintables'].append(fluxtbl)
        prms.write(params, 'parameters.yaml')
        subprocess.run(
            'rm -r {}'.format(params['calibration']['apgaintable']), shell=True, check=True)

        # Applying the calibrations on flux cal
        gaintables = params['calibration']['gaintables']
        for i in fluxcal:
            print('Applying the calibration table to ', i)

            cts.applycal(msfile, field=i, spw=spw, gaintable=gaintables, gainfield=[
                         '', '', i], uvrange=uvran, interp=['', '', 'linear'], calwt=[False], parang=False)

        # Apply the calibration on phase cal
        cts.applycal(msfile, field=phasecal, uvrange=uvran, gaintable=gaintables, gainfield=[
                     '', '', phasecal], interp=['', '', 'linear'], calwt=[False], parang=False)

        # Flagging after calibration

        def clip_est(fluxscale, nsigma, loop, beta):
            return [fluxscale - nsigma/loop**beta, fluxscale + nsigma/loop**beta]

        # fluxscale_list = [15, 22.5, 3.3]
        # uplims_list = [20, 20, 20]
        # beta=[0.5, 0.6, 0.6]
        # tcut_list = [6, 6, 10]
        # fcut_list = [6, 6, 10]
        pcal_flux = np.float(phasecal_flux['1']['0']['fluxd'][0])
        fluxscale_list = params['general']['fluxscale_list']
        fluxscale_list.append(pcal_flux)
        uplims_list = params['flagging']['uplims_list']
        beta = params['flagging']['beta']
        tcut_list = params['flagging']['tcut_list']
        fcut_list = params['flagging']['fcut_list']

        if flagger == 'default':
            for j, i in enumerate(allcals):
                flg.clipper(msfile, params, field=i, cliplevel=clip_est(
                    fluxscale_list[j], uplims_list[j], loop, beta[j]), instance='postcal')
                flg.tfcropper(
                    msfile, params, field=i, tcut=tcut_list[j], fcut=fcut_list[j], instance='postcal')
                flg.extend(msfile, params, field=i,
                           grow=80, instance='postcal')
                print('Flagged', i, 'postcalibration.')
            # Flag the phasecal using rflag
            flg.rflagger(msfile, params, field=phasecal,
                         tcut=10, fcut=10, instance='postcal')
            flg.extend(msfile, params, field=phasecal,
                       grow=80, instance='postcal')

        else:
            print('No flagging.')

        if interactive:
            subprocess.run('casaplotms vis={} field={}'.format(
                msfile, fluxcal[0]), shell=True, check=True)
            flagcal_fin = input(
                'Are you satisfied with the calibration?[y/n] ')
            # Remove the old cal tables before continuing
            for i in gaintables:
                subprocess.run('rm -r {}'.format(i), shell=True, check=True)

            continue
        else:
            print('Flagcal running in automode.')
            niters = niters - 1
            loop = loop + 1

            if niters < 1:
                print('Flagcal loops finished.')
                break
            else:
                # Remove all the old cal tables before continuing.
                print('Clearing the corrected column and fluxcal model...')
                cts.clearcal(msfile)  # Removes the corrected datacolumn
                cts.delmod(msfile)  # Removes the setjy model

                print('Clearing all the gaintables...')
                for i in gaintables:
                    print(i)
                    subprocess.run('rm -r {}'.format(i),
                                   shell=True, check=True)

                continue

    else:
        print('Calibration of flux and phase calibrators done.')

    # apply the calibrations on the target
    target = params['general']['target']
    print('Applying the calibration tables to the target...')
    gaintables = params['calibration']['gaintables']
    cts.applycal(msfile, field=target, uvrange=uvran, gaintable=gaintables, gainfield=[
                 '', '', phasecal], interp=['', '', 'linear'], calwt=[False], parang=False)

    # rflag the data
    print('Mildly Rflagging the target at cutoff of 10 sigma...')
    flg.rflagger(msfile, params, field=target,
                 tcut=10, fcut=10, instance='postcal')
    flg.extend(msfile, params, field=target, grow=80, instance='postcal')

    # split the calibrated target data
    out_cal_file = params['general']['targetcalfile']

    print('Splitting the target...')
    cts.mstransform(msfile, field=target, spw=spw, chanaverage=False,
                    datacolumn='corrected', outputvis=out_cal_file)

    return print('Flagcal script done.')


def flagcal_bl(msfile, params, niters=1, flagger='default', interactive=False):
    '''
    This function takes an initially flagged msfile and goes through the flagging and calibration loops. It does delaycal, bandpass and a amplitude and phase cals. It then flags the data and then continues to the calibration cycle. The loops continue till niters end or in the interactive mode when the user is satisfied. The calibration in then applied to the source and it is mildly flagged using Rflag and splitted in a seperate msfile.
    '''

    fcals = ','.join(fluxcal)  # joining the fluxcals in a casa readable format

    # Main flagcal loops begin

    flagcal_fin = 'n'  # a flag to denote finished flagging
    loop = 1  # Keeping a track of number of iterations
    while flagcal_fin == 'n':
        # Beginning with an empty gaintable list, which will be succesively appended after every calibration.
        gaintables = []
        params['calibration'].update({'gaintables': gaintables})
        # writes the gaintables column in the parameters file.
        prms.write(params, 'parameters.yaml')
        cts.setjy(msfile, field=fcals, scalebychan=True,
                  standard='Perley-Butler 2017', listmodels=False, usescratch=False)

        clb.delaycal(msfile, params, field=fcals)
        # append the caltable and save the params file
        params['calibration']['gaintables'].append(
            params['calibration']['delaytable'])
        prms.write(params, 'parameters.yaml')
        if interactive:
            caltable = params['calibration']['delaytable']
            subprocess.run('casaplotms vis={} field={}'.format(
                caltable, fcals), shell=True, check=True)
            antflag = input(
                "Do you want to flag any antenna(s) ? [y/n] \n If yes, append the bad antennas in the params file now.")
            if antflag == 'y':
                flg.badantflag(msfile, params)
            else:
                print('No flagging after delaycal.')

        else:
            None

        # Using fluxcals for bandpass calibration
        clb.bpasscal(msfile, params, field=fcals)
        params['calibration']['gaintables'].append(
            params['calibration']['bpasstable'])
        prms.write(params, 'parameters.yaml')

        # Joining all the calibrators and doing amplitutde and phase calibration
        phasecal = params['general']['phasecal']
        print('Phasecal is ', phasecal)
        allcals = fluxcal + [phasecal]

        # for i in allcals:
        #    clb.apcal(msfile, params, field=i)

        allcals2 = ','.join(allcals)
        clb.apcal(msfile, params, field=allcals2)

        # Adding the amplitude and phase calibration tables in gaintables
        params['calibration']['gaintables'].append(
            params['calibration']['apgaintable'])
        prms.write(params, 'parameters.yaml')

        # Doing a blcal
        print('Attempting a baseline based calibration. Please check the fluxes carefully.')
        blcal_table = 'blcal.cal'
        cts.blcal(msfile,
                  caltable=blcal_table,  # Output table name
                  field=allcals2,  # A field with a very good model
                  solint='2min',  # single solution per baseline, spw
                  # all prior cal
                  gaintable=params['calibration']['gaintables'],
                  freqdep=False)  # frequency-independent solution

        params['calibration']['gaintables'].append(blcal_table)
        prms.write(params, 'parameters.yaml')

        uvran = params['general']['uvran']

        # GETJY
        print('Setting the absolute fluxscale for ', phasecal)
        fluxtbl = params['calibration']['fluxscaletable']

        phasecal_flux = cts.fluxscale(msfile, caltable=params['calibration']['apgaintable'],
                                      fluxtable=fluxtbl, reference=fcals, transfer=phasecal, incremental=False, append=False)
        print('The flux density of {}'.format(phasecal)+'is',
              phasecal_flux['1']['0']['fluxd'][0], '+/-', phasecal_flux['1']['0']['fluxdErr'][0])
        # Replace the apgaintable with fluxscale table
        params['calibration']['gaintables'].remove(
            params['calibration']['apgaintable'])
        params['calibration']['gaintables'].append(fluxtbl)
        prms.write(params, 'parameters.yaml')
        subprocess.run(
            'rm -r {}'.format(params['calibration']['apgaintable']), shell=True, check=True)

        # Applying the calibrations on flux cal
        gaintables = params['calibration']['gaintables']
        for i in fluxcal:
            print('Applying the calibration tables to ', i)
            print('Gaintables during applying is', gaintables)
            cts.applycal(msfile, field=i, spw=spw, gaintable=gaintables, gainfield=[
                         '', '', i], uvrange=uvran, interp=['', '', 'linear'], calwt=[False], parang=False)

        # Apply the calibration on phase cal
        cts.applycal(msfile, field=phasecal, uvrange=uvran, gaintable=gaintables, gainfield=[
                     '', '', phasecal], interp=['', '', 'linear'], calwt=[False], parang=False)

        # Flagging after calibration

        def clip_est(fluxscale, nsigma, loop, beta):
            return [fluxscale - nsigma/loop**beta, fluxscale + nsigma/loop**beta]

        fluxscale_list = [15, 22.5, 3.3]
        uplims_list = [20, 20, 20]
        beta = [0.5, 0.6, 0.6]
        tcut_list = [6, 6, 10]
        fcut_list = [6, 6, 10]
        if flagger == 'default':
            for j, i in enumerate(allcals):
                flg.clipper(msfile, params, field=i, cliplevel=clip_est(
                    fluxscale_list[j], uplims_list[j], loop, beta[j]), instance='postcal')
                flg.tfcropper(
                    msfile, params, field=i, tcut=tcut_list[j], fcut=fcut_list[j], instance='postcal')
                flg.extend(msfile, params, field=i,
                           grow=80, instance='postcal')
                print('Flagged', i, 'postcalibration.')
            # Flag the phasecal using rflag
            flg.rflagger(msfile, params, field=phasecal,
                         tcut=10, fcut=10, instance='postcal')
            flg.extend(msfile, params, field=phasecal,
                       grow=80, instance='postcal')

        else:
            print('No flagging.')

        if interactive:
            subprocess.run('casaplotms vis={} field={}'.format(
                msfile, fluxcal[0]), shell=True, check=True)
            flagcal_fin = input(
                'Are you satisfied with the calibration?[y/n] ')
            # Remove the old cal tables before continuing
            for i in gaintables:
                subprocess.run('rm -r {}'.format(i), shell=True, check=True)

            continue
        else:
            print('Flagcal running in automode.')
            niters = niters - 1
            loop = loop + 1

            if niters < 1:
                print('Flagcal loops finished.')
                break
            else:
                # Remove all the old cal tables before continuing.
                print('Clearing the corrected column and fluxcal model...')
                cts.clearcal(msfile)  # Removes the corrected datacolumn
                cts.delmod(msfile)  # Removes the setjy model

                print('Clearing all the gaintables...')
                for i in gaintables:
                    subprocess.run('rm -r {}'.format(i),
                                   shell=True, check=True)

                continue

    else:
        print('Calibration of flux and phase calibrators done.')

    # apply the calibrations on the target
    target = params['general']['target']
    print('Applying the calibration tables to the target...')
    gaintables = params['calibration']['gaintables']
    cts.applycal(msfile, field=target, uvrange=uvran, gaintable=gaintables, gainfield=[
                 '', '', phasecal], interp=['', '', 'linear'], calwt=[False], parang=False)

    # rflag the data
    print('Mildly Rflagging the target at cutoff of 10 sigma...')
    flg.rflagger(msfile, params, field=target,
                 tcut=10, fcut=10, instance='postcal')
    flg.extend(msfile, params, field=target, grow=80, instance='postcal')

    # split the calibrated target data
    out_cal_file = params['general']['targetcalfile']

    print('Splitting the target...')
    cts.mstransform(msfile, field=target, spw=spw, chanaverage=False,
                    datacolumn='corrected', outputvis=out_cal_file)

    return print('Flagcal with blcal script done.')


def imagecal(targetcalfile, params, nloops=1, ploops=5, aploops=1, flagger='default', interactive=False):
    '''
    This function takes in a calibrated target file (usually the channel averaged file) and goes through "niters" of imagecal loops. A imagecal loop is defined as first making a image using imgr.tcleaner. Then "ploops" of phase-only self-cal and "aploops" of a&p selfcal. Then the continuum image is subtracted from the UV data and the residuals are flagged. After having gone through all the "niters" loop it spits out a final continuum image.
    '''

    imaging_params = params['imagecal']
    outimage = imaging_params['outimage']
    target = params['general']['target']
    threshold_range = imaging_params['threshold_range']
    threshold_final = imaging_params['threshold_final']
    solints = imaging_params['solints']
    niter_range = imaging_params['niter_range']
    tempdir = params['general']['temp']
    outdir = params['general']['outdir']

    # Preparing the ranges of different parameters for the loops
    solint_range = np.linspace(solints[0], solints[1], ploops)
    solint_range = [str(i)+'min' for i in solint_range]
    threshold_range = np.linspace(
        threshold_range[0], threshold_range[1], ploops)
    threshold_range = [str(i)+'mJy' for i in threshold_range]

    niter_range = np.linspace(niter_range[0], niter_range[1], ploops)
    niter_range = [int(i) for i in niter_range]
    # Initially begin with the avspc file, and then change this file name to the running self-cal file
    sc_ap_msfile = targetcalfile
    nloop_index = 1 + np.arange(nloops)  # The nloop index to the files names

    # Making list to save the relevant stats of the images in the various self-cal looops
    regionfile = params['imagecal']['regionfile']
    type_list = []
    index_list = []
    loop_list = []
    rms_list = []
    peakflux_list = []

    for nindex in nloop_index:
        # subprocess.run('rm -r {}'.format(temp_dir), shell=True, check=True) # Clearing the temp directory
        # subprocess.run('mkdir {}'.format(temp_dir), shell=True, check=True)
        # This gives the index to the cont image and cal files created later
        ploop_index = 1 + np.arange(ploops)
        # start again with the avspcfile ms file name for the next round of self-cals
        sc_p_msfile = targetcalfile
        for pindex in ploop_index:  # Run all the ploops
            print('Self-cal phase-only loop', pindex)
            imgr.tcleaner(sc_p_msfile, params, threshold=threshold_range[pindex - 1], niter=niter_range[pindex - 1],
                          outimage=tempdir+outimage+'_sc_p.'+str(nindex)+str(pindex), interactive=interactive)
            # Adding imstats in the list
            imagename = tempdir+outimage+'_sc_p.' + \
                str(nindex)+str(pindex)+'.image.tt0'
            type_list.append('p')
            loop_list.append(nindex)
            index_list.append(pindex)
            rms, peakflux = stats(imagename, regionfile)
            rms_list.append(rms)
            peakflux_list.append(peakflux)

            clb.selfcal(sc_p_msfile, params, mode='p', in_gaintable=[], out_gaintable=tempdir +
                        'sc_p.gcal.'+str(nindex)+str(pindex), solint=solint_range[pindex - 1], solnorm=False)
            # Change the gaintable to the latest
            gaintable = [tempdir+'sc_p.gcal.'+str(nindex)+str(pindex)]

            cts.applycal(sc_p_msfile, gaintable=gaintable, field='', gainfield='',
                         applymode='calonly', interp=['linear'], calwt=False, parang=False)
            cts.mstransform(sc_p_msfile, field='0', spw='0', datacolumn='corrected',
                            outputvis=tempdir+'sc_p_'+str(nindex)+str(pindex)+'.ms')
            sc_p_msfile = tempdir+'sc_p_'+str(nindex)+str(pindex)+'.ms'

        final_pcal_table = gaintable  # The final pcal table to be returned in the end

        # This gives the index to the cont image and cal files created later
        aploop_index = 1 + np.arange(aploops)
        sc_ap_msfile = sc_p_msfile  # Beginning with the pfile
        niter_ap = niter_range[-1]  # The last object in pcal niters
        threshold_ap = threshold_range[-1]
        solint_ap = solint_range[-1]
        for apindex in aploop_index:  # Run all the aploops
            print('Self-cal a&p loop', apindex)
            imgr.tcleaner(sc_ap_msfile, params, threshold=threshold_ap, niter=niter_ap,
                          outimage=tempdir+outimage+'_sc_ap.'+str(nindex)+str(apindex), interactive=interactive)

            # Adding the self cal ap loop imstats in the list
            imagename = tempdir+outimage+'_sc_ap.' + \
                str(nindex)+str(apindex)+'.image.tt0'
            type_list.append('ap')
            loop_list.append(nindex)
            index_list.append(apindex)
            rms, peakflux = stats(imagename, regionfile)
            rms_list.append(rms)
            peakflux_list.append(peakflux)

            clb.selfcal(sc_ap_msfile, params, mode='a&p', in_gaintable=[], out_gaintable=tempdir +
                        'sc_ap.gcal.'+str(nindex)+str(apindex), solint=solint_ap, solnorm=True)
            # Change the gaintable to the latest
            gaintable = [tempdir+'sc_ap.gcal.'+str(nindex)+str(apindex)]
            cts.applycal(sc_ap_msfile, gaintable=gaintable, field='', gainfield='',
                         applymode='calonly', interp=['linear'], calwt=False, parang=False)
            cts.mstransform(sc_ap_msfile, field='0', spw='0', datacolumn='corrected',
                            outputvis=tempdir+'sc_ap_'+str(nindex)+str(apindex)+'.ms')
            sc_ap_msfile = tempdir+'sc_ap_'+str(nindex)+str(apindex)+'.ms'

        # Create an intermediate model for outlier flagging.
        imaging_params = params['imagecal']
        outimage = imaging_params['outimage']
        target = params['general']['target']
        imsize = imaging_params['imsize']
        cell = imaging_params['cell']
        robust = imaging_params['robust']
        weighting = imaging_params['weighting']
        uvran = imaging_params['uvran']
        uvtaper = imaging_params['uvtaper']
        nterms = imaging_params['nterms']
        niter = 100000  # niter_ap
        threshold = str(threshold_final)+'mJy'
        wprojplanes = imaging_params['wprojplanes']
        scales = imaging_params['scales']

        if nterms > 1:
            cts.tclean(sc_ap_msfile, imagename=tempdir+outimage+'_sc_ap_final.'+str(nindex)+str(apindex), field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                       specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                       minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6,
                       threshold=threshold, aterm=True, pblimit=-1, deconvolver='mtmfs',
                       gridder='wproject', wprojplanes=wprojplanes, scales=scales, wbawp=False,
                       restoration=True, savemodel='modelcolumn', cyclefactor=0.5, parallel=False,
                       interactive=False)
        elif nterms == 1:
            cts.tclean(sc_ap_msfile, imagename=tempdir+outimage+'_sc_ap_final.'+str(nindex)+str(apindex), field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                       specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                       minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6, threshold=threshold,
                       aterm=True, pblimit=-1, deconvolver='multiscale', gridder='wproject',
                       wprojplanes=wprojplanes, scales=scales, wbawp=False, restoration=True,
                       savemodel='modelcolumn', cyclefactor=0.5, parallel=False, interactive=False)

        imagename = tempdir+outimage+'_sc_ap_final.' + \
            str(nindex)+str(apindex)+'.image.tt0'
        type_list.append('final')
        loop_list.append(nindex)
        index_list.append(-99)
        rms, peakflux = stats(imagename, regionfile)
        rms_list.append(rms)
        peakflux_list.append(peakflux)

        '''
        0) Clear all the model and calibration table from the avspc file.
        1) Apply the final calibration table to the avspc file.
        2) Copy the final model to the avspc file,
        3) uvsub --> rflag --> undo-uvsub
        4) Clear the model again
        5) Repeat self-cal
        '''
        print('Clearing the corrected column and the tclean model...')

        cts.clearcal(targetcalfile)  # Removes the corrected datacolumn
        cts.delmod(targetcalfile)  # Removes the tclean model
        cts.applycal(targetcalfile, gaintable=gaintable, field='', gainfield='', applymode='calonly', interp=[
                     'linear'], calwt=False, parang=False)  # Apply the latest calibration table from the last loop
        if nterms == 2:
            cts.ft(targetcalfile, spw='0', nterms=nterms, model=[tempdir+outimage+'_sc_ap_final.'+str(nindex)+str(
                apindex)+'.model.tt0', tempdir+outimage+'_sc_ap_final.'+str(nindex)+str(apindex)+'.model.tt1'], usescratch=True)  # Copy the finale model from the tempfile
        elif nterms == 1:
            cts.ft(targetcalfile, spw='0', nterms=nterms, model=[tempdir+outimage+'_sc_ap_final.'+str(
                nindex)+str(apindex)+'.model.tt0'], usescratch=True)  # Copy the finale model from the tempfile

        cts.uvsub(targetcalfile, reverse=False)
        flg.rflagger(targetcalfile, params, field=target,
                     tcut=6, fcut=6, instance='postcal')
        flg.extend(targetcalfile, params, field=target,
                   grow=80, instance='postcal')
        # Adding the corrected-data and residuals
        cts.uvsub(targetcalfile, reverse=True)

        if nindex == np.max(nloop_index):
            # Dont clear the corrected dataset for the final loop.
            break
        else:
            # Clearcal to start fresh
            cts.clearcal(targetcalfile)  # Removes the corrected datacolumn
            cts.delmod(targetcalfile)  # Removes the tclean model

    t = Table((np.array(loop_list), np.array(type_list), np.array(index_list), np.array(
        rms_list), np.array(peakflux_list)), names=('loop', 'type', 'index', 'rms', 'peakflux'))
    t.write(outdir+'selfcal_table.txt', format='ascii', overwrite=True)

    for i in nloop_index:
        sub_table = t[np.where(t['loop'] == i)[0]]
        markers = ['o', '^', '*']
        index_add = 0
        for k, j in enumerate(['p', 'ap', 'final']):
            sub_subtable = sub_table[np.where(sub_table['type'] == j)[0]]
            if j == 'ap':
                index_add = len(ploop_index)

            elif j == 'final':
                index_add = 100 + len(ploop_index) + len(aploop_index)
            else:
                None
            dyna_range = sub_subtable['peakflux']/sub_subtable['rms']
            plt.plot(sub_subtable['index']+index_add,
                     dyna_range, marker=markers[k])

    plt.xlabel('Self-cal iteration')
    plt.ylabel('Dynamic Range')
    plt.savefig(outdir+'sc_iter.png')

    # Self-cal loops overV
    outdir_ap_gaintable = [outdir+'sc_ap.gcal.'+str(nindex)+str(apindex)]
    outdir_p_gaintable = [outdir+'sc_p.gcal.'+str(nindex)+str(pindex)]

    # cp the final gaintable to the outdir
    subprocess.run(
        'cp -r {} {}'.format(gaintable[0], outdir_ap_gaintable[0]), shell=True, check=True)
    # cp the final gaintable to the outdir
    subprocess.run(
        'cp -r {} {}'.format(final_pcal_table[0], outdir_p_gaintable[0]), shell=True, check=True)
    print('Self-cal loops over.')

    print('Making a final continuum  image...')

    imaging_params = params['imagecal']
    outimage = imaging_params['outimage']
    target = params['general']['target']
    imsize = imaging_params['imsize']
    cell = imaging_params['cell']
    robust = imaging_params['robust']
    weighting = imaging_params['weighting']
    uvran = imaging_params['uvran']
    uvtaper = imaging_params['uvtaper']
    nterms = imaging_params['nterms']
    niter = 100000  # niter_ap
    threshold = str(threshold_final)+'mJy'
    wprojplanes = imaging_params['wprojplanes']
    scales = imaging_params['scales']
    final_image = outdir+outimage+'_final'

    if nterms > 1:
        cts.tclean(sc_ap_msfile, imagename=final_image, field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                   specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                   minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6,
                   threshold=threshold, aterm=True, pblimit=-1, deconvolver='mtmfs',
                   gridder='wproject', wprojplanes=wprojplanes, scales=scales, wbawp=False,
                   restoration=True, savemodel='modelcolumn', cyclefactor=0.5, parallel=False,
                   interactive=False)
    elif nterms == 1:
        cts.tclean(sc_ap_msfile, imagename=final_image, field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                   specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                   minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6, threshold=threshold,
                   aterm=True, pblimit=-1, deconvolver='multiscale', gridder='wproject',
                   wprojplanes=wprojplanes, scales=scales, wbawp=False, restoration=True,
                   savemodel='modelcolumn', cyclefactor=0.5, parallel=False, interactive=False)

    print('Imaging and self-calibration done.')

    return final_image, outdir_p_gaintable+outdir_ap_gaintable


def imagecal2(targetcalfile, params, nloops=1, ploops=5, aploops=1, flagger='default', interactive=False):
    '''
    This function takes in a calibrated target file (usually the channel averaged file) and goes through "niters" of imagecal loops. A imagecal loop is defined as first making a image using imgr.tcleaner. Then "ploops" of phase-only self-cal and "aploops" of a&p selfcal. Then the continuum image is subtracted from the UV data and the residuals are flagged. After having gone through all the "niters" loop it spits out a final continuum image.
    This version doesnt make several ms files.
    '''

    imaging_params = params['imagecal']
    outimage = imaging_params['outimage']
    target = params['general']['target']
    threshold_range = imaging_params['threshold_range']
    threshold_final = imaging_params['threshold_final']
    solints = imaging_params['solints']
    niter_range = imaging_params['niter_range']
    tempdir = params['general']['temp']
    outdir = params['general']['outdir']

    # Preparing the ranges of different parameters for the loops
    solint_range = np.linspace(solints[0], solints[1], ploops)
    solint_range = [str(i)+'min' for i in solint_range]
    threshold_range = np.linspace(
        threshold_range[0], threshold_range[1], ploops)
    threshold_range = [str(i)+'mJy' for i in threshold_range]

    niter_range = np.linspace(niter_range[0], niter_range[1], ploops)
    niter_range = [int(i) for i in niter_range]
    # sc_ap_msfile = targetcalfile # Initially begin with the avspc file, and then change this file name to the running self-cal file
    nloop_index = 1 + np.arange(nloops)  # The nloop index to the files names

    # Making list to save the relevant stats of the images in the various self-cal looops
    regionfile = params['imagecal']['regionfile']
    type_list = []
    index_list = []
    loop_list = []
    rms_list = []
    peakflux_list = []

    for nindex in nloop_index:
        # subprocess.run('rm -r {}'.format(temp_dir), shell=True, check=True) # Clearing the temp directory
        # subprocess.run('mkdir {}'.format(temp_dir), shell=True, check=True)
        # This gives the index to the cal files created later
        ploop_index = 1 + np.arange(ploops)

        for pindex in ploop_index:  # Run all the ploops
            print('Self-cal phase-only loop', pindex)
            imgr.tcleaner(targetcalfile, params, threshold=threshold_range[pindex - 1], niter=niter_range[pindex - 1],
                          outimage=tempdir+outimage+'_sc_p.'+str(nindex)+str(pindex), interactive=interactive)
            # Adding imstats in the list
            imagename = tempdir+outimage+'_sc_p.' + \
                str(nindex)+str(pindex)+'.image.tt0'
            type_list.append('p')
            loop_list.append(nindex)
            index_list.append(pindex)
            rms, peakflux = stats(imagename, regionfile)
            rms_list.append(rms)
            peakflux_list.append(peakflux)

            clb.selfcal(targetcalfile, params, mode='p', in_gaintable=[], out_gaintable=tempdir +
                        'sc_p.gcal.'+str(nindex)+str(pindex), solint=solint_range[pindex - 1], solnorm=False)
            # Change the gaintable to the latest
            gaintable = [tempdir+'sc_p.gcal.'+str(nindex)+str(pindex)]
            cts.applycal(targetcalfile, gaintable=gaintable, field='', gainfield='',
                         applymode='calonly', interp=['linear'], calwt=False, parang=False)

        final_pcal_table = [tempdir+'sc_p.gcal.'+str(nindex)+str(pindex)]

        # This gives the index to the cont image and cal files created later
        aploop_index = 1 + np.arange(aploops)
        niter_ap = niter_range[-1]  # The last object in pcal niters
        threshold_ap = threshold_range[-1]
        solint_ap = 'inf'
        for apindex in aploop_index:  # Run all the aploops
            print('Self-cal a&p loop', apindex)
            imgr.tcleaner(targetcalfile, params, threshold=threshold_ap, niter=niter_ap,
                          outimage=tempdir+outimage+'_sc_ap.'+str(nindex)+str(apindex), interactive=interactive)

            # Adding the self cal ap loop imstats in the list
            imagename = tempdir+outimage+'_sc_ap.' + \
                str(nindex)+str(apindex)+'.image.tt0'
            type_list.append('ap')
            loop_list.append(nindex)
            index_list.append(apindex)
            rms, peakflux = stats(imagename, regionfile)
            rms_list.append(rms)
            peakflux_list.append(peakflux)

            clb.selfcal(targetcalfile, params, mode='a&p', in_gaintable=[
            ], out_gaintable=tempdir+'sc_ap.gcal.'+str(nindex)+str(apindex), solint=solint_ap, solnorm=True)
            # Change the gaintable to the latest, this will also have the phaseonly calibration solutions applied.
            gaintable = final_pcal_table + \
                [tempdir+'sc_ap.gcal.'+str(nindex)+str(apindex)]
            cts.applycal(targetcalfile, gaintable=gaintable, field='', gainfield='',
                         applymode='calonly', interp=['linear'], calwt=False, parang=False)

        # Create an intermediate model for outlier flagging.
        imaging_params = params['imagecal']
        outimage = imaging_params['outimage']
        target = params['general']['target']
        imsize = imaging_params['imsize']
        cell = imaging_params['cell']
        robust = imaging_params['robust']
        weighting = imaging_params['weighting']
        uvran = imaging_params['uvran']
        uvtaper = imaging_params['uvtaper']
        nterms = imaging_params['nterms']
        niter = 100000  # niter_ap
        threshold = str(threshold_final)+'mJy'
        wprojplanes = imaging_params['wprojplanes']
        scales = imaging_params['scales']

        if nterms > 1:
            cts.tclean(targetcalfile, imagename=tempdir+outimage+'_sc_ap_final.'+str(nindex)+str(apindex), field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                       specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                       minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6,
                       threshold=threshold, aterm=True, pblimit=-1, deconvolver='mtmfs',
                       gridder='wproject', wprojplanes=wprojplanes, scales=scales, wbawp=False,
                       restoration=True, savemodel='modelcolumn', cyclefactor=0.5, parallel=False,
                       interactive=False)
        elif nterms == 1:
            cts.tclean(targetcalfile, imagename=tempdir+outimage+'_sc_ap_final.'+str(nindex)+str(apindex), field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                       specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                       minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6, threshold=threshold,
                       aterm=True, pblimit=-1, deconvolver='multiscale', gridder='wproject',
                       wprojplanes=wprojplanes, scales=scales, wbawp=False, restoration=True,
                       savemodel='modelcolumn', cyclefactor=0.5, parallel=False, interactive=False)

        imagename = tempdir+outimage+'_sc_ap_final.' + \
            str(nindex)+str(apindex)+'.image.tt0'
        type_list.append('final')
        loop_list.append(nindex)
        index_list.append(-99)
        rms, peakflux = stats(imagename, regionfile)
        rms_list.append(rms)
        peakflux_list.append(peakflux)

        '''
        1) uvsub --> rflag --> undo-uvsub
        2) Clear the model again
        3) Repeat self-cal
        '''
        print('uvsub and rflagging the data...')

        cts.uvsub(targetcalfile, reverse=False)
        flg.rflagger(targetcalfile, params, field=target,
                     tcut=6, fcut=6, instance='postcal')
        flg.extend(targetcalfile, params, field=target,
                   grow=80, instance='postcal')
        # Adding the corrected-data and residuals
        cts.uvsub(targetcalfile, reverse=True)

    t = Table((np.array(loop_list), np.array(type_list), np.array(index_list), np.array(
        rms_list), np.array(peakflux_list)), names=('loop', 'type', 'index', 'rms', 'peakflux'))
    t.write(outdir+'selfcal_table.txt', format='ascii', overwrite=True)

    for i in nloop_index:
        sub_table = t[np.where(t['loop'] == i)[0]]
        markers = ['o', '^', '*']
        index_add = 0
        for k, j in enumerate(['p', 'ap', 'final']):
            sub_subtable = sub_table[np.where(sub_table['type'] == j)[0]]
            if j == 'ap':
                index_add = len(ploop_index)

            elif j == 'final':
                index_add = 100 + len(ploop_index) + len(aploop_index)
            else:
                None
            dyna_range = sub_subtable['peakflux']/sub_subtable['rms']
            plt.plot(sub_subtable['index']+index_add,
                     dyna_range, marker=markers[k])

    plt.xlabel('Self-cal iteration')
    plt.ylabel('Dynamic Range')
    plt.savefig(outdir+'sc_iter.png')

    # Self-cal loops overV
    outdir_ap_gaintable = [outdir+'sc_ap.gcal.'+str(nindex)+str(apindex)]
    outdir_p_gaintable = [outdir+'sc_p.gcal.'+str(nindex)+str(pindex)]

    # cp the final gaintable to the outdir
    subprocess.run(
        'cp -r {} {}'.format(gaintable[0], outdir_ap_gaintable[0]), shell=True, check=True)
    # cp the final gaintable to the outdir
    subprocess.run(
        'cp -r {} {}'.format(final_pcal_table[0], outdir_p_gaintable[0]), shell=True, check=True)
    print('Self-cal loops over.')

    print('Making a final continuum  image...')

    imaging_params = params['imagecal']
    outimage = imaging_params['outimage']
    target = params['general']['target']
    imsize = imaging_params['imsize']
    cell = imaging_params['cell']
    robust = imaging_params['robust']
    weighting = imaging_params['weighting']
    uvran = imaging_params['uvran']
    uvtaper = imaging_params['uvtaper']
    nterms = imaging_params['nterms']
    niter = 100000  # niter_ap
    threshold = str(threshold_final)+'mJy'
    wprojplanes = imaging_params['wprojplanes']
    scales = imaging_params['scales']
    final_image = outdir+outimage+'_final'

    if nterms > 1:
        cts.tclean(targetcalfile, imagename=final_image, field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                   specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                   minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6,
                   threshold=threshold, aterm=True, pblimit=-1, deconvolver='mtmfs',
                   gridder='wproject', wprojplanes=wprojplanes, scales=scales, wbawp=False,
                   restoration=True, savemodel='modelcolumn', cyclefactor=0.5, parallel=False,
                   interactive=False)
    elif nterms == 1:
        cts.tclean(targetcalfile, imagename=final_image, field=target, spw='0', imsize=imsize, cell=cell,                   robust=robust, weighting=weighting, uvrange=uvran, uvtaper=uvtaper,
                   specmode='mfs', nterms=nterms, niter=niter, usemask='auto-multithresh',
                   minbeamfrac=0.1, sidelobethreshold=1.5, smallscalebias=0.6, threshold=threshold,
                   aterm=True, pblimit=-1, deconvolver='multiscale', gridder='wproject',
                   wprojplanes=wprojplanes, scales=scales, wbawp=False, restoration=True,
                   savemodel='modelcolumn', cyclefactor=0.5, parallel=False, interactive=False)

    print('Imaging and self-calibration done.')

    return final_image, outdir_p_gaintable+outdir_ap_gaintable
