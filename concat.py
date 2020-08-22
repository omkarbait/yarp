import casatasks as cts

msfile1 = '/Data/omkar/HI_DATA/quenched_hi/AGC203001/scan1/AGC203001_scan1_yarp_cal.ms'
msfile2 = '/Data/omkar/HI_DATA/quenched_hi/AGC203001/scan2/AGC203001_scan2_yarp_cal.ms'

outms = '/Data/omkar/HI_DATA/quenched_hi/AGC203001/AGC203001_concat.ms'

cts.concat(vis=[msfile1,msfile2], concatvis=outms)

