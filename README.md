# yarp v0.9.0
Yet Another Radio data reduction Pipeline (yarp)

## CASA-6.0 installation notes for Ubuntu 18.04

Create a virtual environment as given in the CASA site. Then update pip to the lastest: 

sudo pip3 install -U pip

Then pip install casatools. Sometimes you might have a problem with the hashes. In that case download the casatools wheel and manually install it. 

There were no problems noted while installing casatasks. Next installing casampi. 

Make sure you have openmpi. If not, install:

sudo apt-get install -y openmpi-bin openmpi-docs libopenmpi-dev mpi

Then pip install casampi as shown on the CASA site.   

## CASA pipeline instructions

Here I will briefly describe and write notes on the various scripts I have written for CASA. This will help in assimilating them all in the future. 

The pipeline consists of several scripts e.g., flagcal, contimg etc. Each script consists of several recipes (python modules). 


Before starting we need to convert LTA files to FITS using ltabin and gvfits using the following commands:

1) listscan <filename>_gwb.lta

After this edit the FITS column in the .log file to a suitable name for the output filts file. 

2) gvfits <filename>.log

If you first want to run flagcal do:

flagcal fits_in=input.fits 

## This script does the following steps:

1) intial_inspection.py: 

Right now this scripts plots the various antenna locations and  saves it in the ants/ folder. It then runs the listobs and saves the output in a text files in the listobs/ folder. It then plots the Amp vs. channel data for one of the fluxcal. This can be used to select a good channel for initial flagging and calibrations. It then plots the visibilities as a function of time iterating over all antennas for each of the fluxcal and saves the output in the ants/ folder. It then asks for a user input of all the bad antennas, which it then flags. 

2) flagcal.py:
   Done !

3) Make a test cube image or a average spec to identify line channels <To be added>

4) imagecal (imaging and self-cal)
   Done. Several things can be changed here. 

1) Keep the niter to 10000 and only use threshold to reach the required rms.

2) uvsub --> rflag --> seflcal and repeat

Play with different robust values during the selfcal loop and a different during the final image. 

IMP: Check for convergence in selfcal. 

Flag after applying selfcal. rflag the line free channels to 6 sigma, and the line channels to 10 sigma. 


5) continuum_sub: subtracting the model using the ft task. Then do uvcontsub. 

6) cube_image.py: Use sofia for masking. 


## The future

The workflow is ready in the form of a pipeline. Use ruffus to fuse together all the scripts in a workflow. 

### Acknowledgements
Some of the initial developement of this pipeline took some inspiration from the [CAPTURE pipeline](https://github.com/ruta-k/uGMRT-pipeline) designed for the uGMRT continuum data reduction. The extensive [VLA data reduction tutorials](https://casaguides.nrao.edu/index.php?title=Main_Page) and the [Radio Astronomy School 2019](http://www.ncra.tifr.res.in/~ruta/ras2019/CASA-tutorial.html) tutorials came out to be very useful in writing this pipeline. Nissim's AIPS.INFO also came out to be handy. I would also like to thank Sushma Kurapati and Biny Sebastian for useful dicussions which helped in improving this pipeline. 
