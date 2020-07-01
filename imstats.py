import casatasks as cts

def stats(imagefile, regionfile):
    
    stats1 = cts.imstat(imagefile, stokes='I') 
    peakflux = stats1['max'][0]
    stats2 = cts.imstat(imagefile, region=regionfile)
    rms = stats2['rms'][0]

    return rms, peakflux
