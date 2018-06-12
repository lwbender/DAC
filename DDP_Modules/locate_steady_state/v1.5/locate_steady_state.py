#--------------------------------------------------
# locate_steady_state_v1.5
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
def locate_steady_state(data, SS_win, verbose = False, debug = False):
    if verbose: print('Steady State Determination: Initialized', end = dash)
    #~
    samp = pd.DataFrame()
    CIs = ['CI_PC{}'.format(k) for k in [2,4,5,6]]
    data = data.copy()
    data['SS'] = np.nan
    SS_count = 0
    SS_flg = True
    #~
    for i, z in enumerate(data.index):
        samp = samp.append(data.iloc[i])    
        if len(samp)<SS_win: continue #check sample size is greater than window
        #~
        for c in CIs: #check for stable clusters 
            if len(np.unique(samp[c]))>1: #number of unique clusters in PC of 'c'
                samp = samp.iloc[-4:]
                SS_flg = True
                break
        #~
        if (c == CIs[-1]) & (len(samp)>4): #if criterias passed, label steady state
            if SS_flg:
                SS_count += 1
                SS_flg = False
            data.loc[samp.index.tolist(),'SS'] = SS_count
    #~
    data['type']='steady_state'
    #~
    if verbose: print('Steady States Located: ' + str(SS_count))
    if verbose: print(dash[1:] + 'Steady State Determination: Completed', end = dash)
    return data