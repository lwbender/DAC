#--------------------------------------------------
# locate_steady_state_v1.3
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
def locate_steady_state(cluster_data,win_size, verbose = False, debug = False):
    samp=pd.DataFrame()
    clus = ['PC{}_cluster'.format(k) for k in [2,4,5,6]]
    SS_data=cluster_data.copy()
    SS_data['SS']=np.nan
    SS_count=0
    SS_flg=True
    for i,meas in enumerate(cluster_data.PC2):
        samp=samp.append(cluster_data.iloc[i])
    
        if len(samp)<win_size: 
            if debug: print('not long enough '+str(i+1))
            continue
        
        if debug: print('long enough now '+str(i+1))
        for c in clus:    
            if len(np.unique(samp[c]))>1: #number of unique clusters in PC of 'c'
                if debug: print('bad SS '+str(i+1))
                if debug: print (samp[clus])
                samp = samp.iloc[-4:]
                SS_flg=True
                break
                
        if (c == clus[-1]) & (len(samp)>4):
            if SS_flg:
                SS_count+=1
                SS_flg=False
            if debug: print('okay got SS '+str(i+1))
            if debug: print (samp[clus])
            SS_data.loc[samp.index,'SS']=SS_count
    SS_data['Mversion']='v1.3'
    return SS_data
