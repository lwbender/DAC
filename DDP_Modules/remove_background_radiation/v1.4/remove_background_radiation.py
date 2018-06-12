#--------------------------------------------------
# remove_background_radation_v1.4
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
def remove_background_radiation(data, BGRad, BRAFs, verbose = False, debug = False):
    if verbose: print('Background Radiation Removal: Initialized', end = dash)
    #~
    data = data.copy()
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC1-PC7
    PCi = (data.index - data.index[0]).total_seconds()/24/60/60 #in days
    #~
    #remove background dose
    for i, PC in enumerate(PCs):
        data[PC] = data[PC] - PCi*BGRad*BRAFs[PC]
        data['BRAF_' + PC] = BRAFs[PC]
    data['BGRad'] = BGRad
    data['Mversion'] = 'v1.4'
    data['type'] = 'bkgd_rad_removed'
    #~
    if verbose: print('Background Radiation Removal: Completed', end = dash)
    return data