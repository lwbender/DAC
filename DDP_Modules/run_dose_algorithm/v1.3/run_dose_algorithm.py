#--------------------------------------------------
# run_dose_algorithm_v1.3
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
import DDP_dose_algorithm
dose_algorithm = DDP_dose_algorithm.dose_algorithm
#~
dash='\n'+'-'*59+'\n'
pd.options.mode.chained_assignment = None  # default='warn'

##
def run_dose_algorithm(SS_data, MRD, verbose = False, debug = False):
    #calculate average dCap at each step (find CVs by substracting current SS with previous) --data['PCx_SS']
    #calculate individual changes in dose -- data['dSDE']
    #calculate accumulated dose -- data['SDE']
    data=SS_data.copy()
    SSs=pd.unique(data.SS)
    data['SDE']=np.nan
    data['DDE']=np.nan
    data['LDE']=np.nan
    data['dSDE']=np.nan
    data['dDDE']=np.nan
    data['dLDE']=np.nan
    data['EnergyEst']=np.nan
    data['Rad_Quality']=np.nan
    cols = ['PC{}'.format(k) for k in [2,4,5,6]]

    for c in cols: data['CV_'+c]=np.nan
    if (len(SSs)==1) & (numpy.isnan(SSs[0])): 
        return data
    else:
        SSs = SSs[~numpy.isnan(SSs)]
    
        for i,sstate in enumerate(SSs):
            #current steady state
            sample=data[data.SS==SSs[i]]
            #if it's not the first steady state, get previous steady state
            if (i!=0): 
                prev_samp=data[data.SS==SSs[i-1]]
                prev_SDE=data[data.SS==SSs[i-1]].SDE.values[0]
                prev_DDE=data[data.SS==SSs[i-1]].DDE.values[0]
                prev_LDE=data[data.SS==SSs[i-1]].LDE.values[0]
    
            #set CVs for ss
            for c in cols:
                data.loc[sample.index,'CV_'+c]=np.mean(sample[c][:5])
    
            # if it is first SS, then set dose = zero, else calculate accumulated dose
            if i==0: 
                data.loc[sample.index,'SDE']=0
                data.loc[sample.index,'DDE']=0
                data.loc[sample.index,'LDE']=0
                data.loc[sample.index,'dSDE']=0
                data.loc[sample.index,'dDDE']=0
                data.loc[sample.index,'dLDE']=0
                continue
        
                #cvs is CVs current - CVs prev    
            cvs=np.mean(sample[cols][:5])-np.mean(prev_samp[cols][:5])
            da_output=get_dose(cvs,'v1.3')
            if da_output[0] <MRD:
                
                data.SDE[sample.index]=prev_SDE          
                data.dSDE[sample.index]=0
                #
                data.DDE[sample.index]=prev_DDE        
                data.dDDE[sample.index]=0
                #
                data.LDE[sample.index]=prev_LDE         
                data.dLDE[sample.index]=0
                #
                for c in cols: data.loc[sample.index,c]=np.mean(prev_samp[c][:5])
            else:
                #set dose with dose algorithm
                data.loc[sample.index,'SDE']=prev_SDE+da_output[0]          
                data.loc[sample.index,'dSDE']=da_output[0]
                #
                data.loc[sample.index,'DDE']=prev_DDE+da_output[1]          
                data.loc[sample.index,'dDDE']=da_output[1]
                #
                data.loc[sample.index,'LDE']=prev_LDE+da_output[2]          
                data.loc[sample.index,'dLDE']=da_output[2]
                data.loc[sample.index,'EnergyEst']=da_output[3]
                data.loc[sample.index,'Rad_Quality']=da_output[4]
    data['Mversion']='v1.3'
    return data

##
def get_dose(cvs,version):
            CV2 = cvs[0]
            CV4 = cvs[1]
            CV5 = cvs[2]
            CV6 = cvs[3]
            SDE, DDE, LDE, EnergyEst, Rad_Quality = dose_algorithm(CV2, CV4, CV5, CV6,Mversion = version)
            return SDE, DDE, LDE, EnergyEst, Rad_Quality
