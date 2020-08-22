# This module contains several flagging recipes.
import subprocess
import casatasks as cts

def uvsubber(msfile, params, fitspw, nterms, model_image=['image.model.tt0','image.model.tt1']):
    
    # Convert a model and fill in the model column of the msfile
    ft(vis=msfile, spw=0, nterms=nterms, model=['image.model.tt0','image.model.tt1'], usescratch=False) 

    # Do a uvsub

    # Split out the uvsub file

    # undo uvsub of the outputfile

    # uvcontsub to remove residual continuum 
