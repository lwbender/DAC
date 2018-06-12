#--------------------------------------------------
# convert_to_dose_v1.4
#--------------------------------------------------
#~
#--------------------------------------------------
# Standard imports & definitions
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

#~
#--------------------------------------------------
def convert_to_dose(data, Ss, SAFs, verbose = False, debug = False):
    if verbose: print('Dose Conversion: Initialized', end = dash)
    #~
    data = data.copy()
    #convert to dose in millirem
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC2,4,5,6
    for PC in PCs:
        data[PC] = data[PC] / (Ss[PC]*SAFs[PC])
        data['S_' + PC] = Ss[PC]
        data['SAF_' + PC] = SAFs[PC]
    #~
    data['Mversion'] = 'v1.4'
    data['type'] = 'dose'
    #~
    if verbose: print('Dose Conversion: Completed', end = dash)
    return data
