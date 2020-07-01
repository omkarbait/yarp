import parameters as prms
import flagger as flg
import calibrator as clb
import casatasks as cts
import subprocess
from  recipes import flagcal

params = prms.read('parameters.yaml')

general_params = params['general'] # loading general params
msfile = general_params['msfile']
outdir = general_params['outdir']
fluxcal= general_params['fluxcal']

def pipeline(msfile, params, doinitial_flagging=True, dodelaycal=True, dobpass=True, doflagcal=True, docont_image=True):
    
    '''
    This function takes combines several recipes to construct a pipeline. In particular here it follows a simple procedure. 

    initial flagging --> setjy+delay calibration --> amplitude calibration + flagging loops on calibrators --> bandpass calibration + flagging loops --> imaging+selfcal loops --> final image --> UVSUB+CVEL --> Cube image with source finder. 
    ''' 

    print('Running yarrp pipeline ...')
    gaintables = []
    params['calibration'].update({'gaintables': gaintables})
    prms.write(params, 'parameters.yaml')


    if doinitial_flagging:
        flg.badantflag(msfile, params)
        flg.aoflagger(msfile, params)
    else:
        print('No initial flagging this time.')
        
    fcals = ','.join(fluxcal) # joining the fluxcals in a casa readable format
    cts.setjy(msfile, field=fcals, scalebychan=True, standard='Perley-Butler 2017', listmodels=False, usescratch=False)
     
    if dodelaycal:
        flagcal(msfile, params, field=fcals, flagger='manual', calibrator=clb.delaycal, niters=1, interactive=False)
        #append the caltable and save the params file
        params['calibration']['gaintables'].append(params['calibration']['delaytable'])
        prms.write(params, 'parameters.yaml')
    else:
        print('No delay calibration this time.')
    
    if dobpass:
         
        flagcal(msfile, params, field=fcals, flagger='default', niters=1, calibrator=clb.bpasscal)
        params['calibration']['gaintables'].append(params['calibration']['bpasstable'])
        prms.write(params, 'parameters.yaml')
        
    else:
        print('No flagcal this time.')
    
    if docont_image:
        None

    
    
    
    return print('')


if __name__ == "__main__":
    pipeline(msfile, params, doinitial_flagging=False, dodelaycal=True, dobpass=True, doflagcal=False, docont_image=False)

