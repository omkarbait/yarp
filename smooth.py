import casatasks as cts
import parameters as prms

params = prms.read('parameters.yaml')
outdir = params['general']['outdir']    
target = params['general']['target']
vel_res1 = params['cube']['vel_res']
vel_res = str(vel_res1)+'km/s'
#vel_res = '-14km/s'
file_name = str(vel_res1)+'kmps'
uvran = '0.5~5klambda'
imagename = outdir+target+'_cube_'+str(file_name)+'/'+'uvran_'+str(uvran)+'.image'


print(imagename)
# Gauss smooth the image
bmaj = cts.imhead(imagename, mode='get', hdkey='BMAJ')['value']
bmin = cts.imhead(imagename, mode='get', hdkey='BMIN')['value']
pa = cts.imhead(imagename, mode='get', hdkey='BPA')['value']

bmaj = str(bmaj)+'arcsec'
bmin = str(bmin)+'arcsec'
pa = str(pa)+'deg'
print('Smoothening the image with a beam of ', bmaj, bmin, pa)

cts.imsmooth(imagename=imagename, kernel='gauss', major=bmaj, minor=bmin, pa=pa, outfile=imagename+'_smooth.im', overwrite=True)


# Hanning smooth the spectrum
print('Hanning smoothening with a width of 2.')
cts.specsmooth(imagename=imagename+'_smooth.im', outfile=imagename+'_hanningsmooth.im', function="hanning", dmethod="", width=2, overwrite=True)


