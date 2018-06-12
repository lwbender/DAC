#--------------------------------------------------
# remove_background_radation_v1.3
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
def remove_background_radiation(data, BR_base, BRs, verbose = False, debug = False):
    #~
    if verbose: print(dash+'Background Radiation Removal: Initialized',end=dash)
    #~
    data=data.copy()
    #standard definitions
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC1-PC7
    PCi=(data.index-data.index[0]).total_seconds()
    #~
    #remove background dose
    for i, PC in enumerate(PCs):
        data[PC] = data[PC]-PCi*BR_base*BRs[PC]/24/60/60 #Time is in seconds
        data[PC+'_BR']=BRs[PC]
    data['BR_base']=BR_base
    #~
    if verbose: print('Background Radiation Removal: Completed',end=dash)
    #~
    data['Mversion']='v1.3'
    return data
