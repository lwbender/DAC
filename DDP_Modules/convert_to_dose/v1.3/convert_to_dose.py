#--------------------------------------------------
# convert_to_dose_v1.3
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
def convert_to_dose(data, Ss, SAFs, verbose = False, debug = False):
    #~
    if verbose: print(dash+'Dose Conversion: Initialized',end=dash)
    #~
    data=data.copy()
    #convert to dose in millirem
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC1-PC6
    for PC in PCs:
        data[PC] = data[PC] / (Ss[PC]*SAFs[PC] )
        data['S_'+PC]=Ss[PC]
        data['SAF_'+PC]=SAFs[PC]
    #~
    #start dose at zero
    data[PCs] = data[PCs] - (data[PCs].iloc[0])
    #~
    if verbose: print('Dose Conversion: Completed',end=dash)
    #~
    data['Mversion']='v1.3'
    return data
