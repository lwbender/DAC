#--------------------------------------------------
# convert_raw_vals_v1.3
#--------------------------------------------------

## Standard imports & definitions
import os
import sys
import numpy
import numpy as np
import pylab as plt
from datetime import datetime
import pandas
import pandas as pd
#~
dash='\n'+'-'*59+'\n'
pd.options.mode.chained_assignment = None  # default='warn'

##
def convert_raw_vals(data, verbose = False, debug = False):
    #~
    if verbose: print(dash+'Raw data Conversion: Initialized',end=dash)
    #~
    data=data.copy()
    #convert PCs to capacitance values
    PCs = ['PC{}'.format(k) for k in range(1,7)] #PC1-PC6
    data[PCs] = data[PCs]/2**21*220000
    data['PC7']=data['PC7']/2**21
    #~
    #calculate temperature in celsius using TM correction
    a=30.0581251
    b=9.93398982
    c=.0728194191
    d=-0.0484675559
    #~
    #linearization of Thermistor response per actual temp
    temp_lin= (1/(numpy.log(data.PC7)**4) + numpy.log(data.PC7))
    temp_celsius = (a + (b*temp_lin))/ (1 + (c*temp_lin )+ (d*temp_lin**2) )    #temperature in celsius
    #~
    data['temp_c']=temp_celsius
    #~
    if verbose: print('Raw data Conversion: Completed',end=dash)
    #~
    data['Mversion']='v1.3'
    return data
