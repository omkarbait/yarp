import casatasks as cts
import parameters as prms


params = prms.read('parameters.yaml')
general_params = params['general']  # loading general params
msfile = general_params['msfile']
outdir = general_params['outdir']


chans = '26~100;115~230'# channels where continuum has to be estimated and subtracted
imagename = outdir+'AGC203001_cube_14kmps/uvran_0.5~6klambda.image'
line_image = outdir+'AGC203001_cube_14kmps/uvran_0.5~6klambda_imlin.image'
cont_image = outdir+'AGC203001_cube_14kmps/uvran_0.5~6klambda_cont.image'

cts.imcontsub(imagename=imagename, linefile=line_image, contfile=cont_image, fitorder=2, stokes="I")

