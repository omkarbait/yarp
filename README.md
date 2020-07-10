# yarp
<<<<<<< HEAD
Yet Another Radio data reduction Pipeline (yarp) is a modular CASA 6.0 based radio data reduction module. The current focus of this pipeline is to provide a modular environment for reduction raw interferometric radio data, mainly for HI imaging of nearby galaxies. This is mainly possible due to the purely Pythonic framework provided by CASA 6.0. This is a development version with several attempts being made to make the pipeline as modular as possible. 

## Requirements 
Currently there is no installation required for running this pipeline. Simply clone the repository and start using it. However, the following packages are required before running yarp:

- `casa 6.0`
- `astropy` 
- `PyYAML`
=======
Yet Another Radio data reduction Pipeline (yarp).
>>>>>>> f744cee68bd8c4bb71cc79449e0298b0a1aa1313


## CASA-6.0 installation notes for Ubuntu 18.04

This pipeline is mainly tested on Ubuntu 18.04. Use the latest `pip`:
```
python3 -m pip install -U pip
```
This install `casatools` and `casatasks` following the [casa 6.0 installation guide](https://casa.nrao.edu/casadocs/casa-5.6.0/introduction/casa6-installation-and-usage). Using `casampi` can speed things up.

First make sure you have openmpi. If not, install:
```
apt-get install -y openmpi-bin openmpi-docs libopenmpi-dev mpi
```
Then `pip` install `casampi`.   

### Problems

Sometimes `casatools` maynot install in one go. In this manually download the `casatools` wheel and then install it using `pip`. 

## yarp Usage and documentation

A detailed documentation for yarp is under construction. Here I will give a brief overview on the usage.  

Before starting anything we need to convert the LTA files to FITS using ltabin and gvfits using the following commands:

1. `listscan <filename>_gwb.lta`

After this edit the FITS column in the `.log` file to a suitable name for the output filts file. 

2. `gvfits <filename>.log`

If you first want to run Jayaram's `flagcal` do:

```flagcal fits_in=input.fits```

Then finally convert the `.FITS` file to `.MS` using the `importgmrt.py` script. First simply change the locations of the input `.FITS` file and the output `.ms` files and then run:
```
python3 importgmrt.py
```
Before running the yarp pipeline the most important step is to fill in the `parameters.yaml` file. Here initially only fill in the `msfile` and `outdir` variables in the `general` section. Then run:
```
python3 initial_inspection.py
```
This will create a `listobs.txt` file in the `outdir/listscan/` folder. Use this to finally complete the `general` section in the `parameters.yaml` file. Next open the `yarp_planner.ipynb` to follow all the steps there. This will finally help you in filling all the sections related to the imaging, uvsubtraction and cubeimaging in the `parameters.yaml` file. 

yarp consists of  major steps:

- initial flagging. In this step several bad antennas are flagged and the data is quacked, edge channels flagged and the entire data is tfcroped.
- flagcal. This is the main intial flagging and calibration 



Each script consists of several recipes (python modules). 

This script does the following steps:

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
