#--------------------------------------------------
# run_dose_algorithm_v1.5
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
import DDP_dose_algorithm
dose_algorithm = DDP_dose_algorithm.dose_algorithm
#~
dash='\n'+'-'*59+'\n'
pd.options.mode.chained_assignment = None  # default='warn'

#~
#--------------------------------------------------
def run_dose_algorithm(data, pCVs, prev_SDE, prev_DDE, prev_LDE, MRD, DAversion, verbose = False, debug = False):
    if verbose: print('Dose Calculation: Initialized', end = dash)
    #calculate average dCap at each step (find CVs by substracting current SS with previous)
    #calculate individual changes in dose -- data['dSDE']
    #calculate accumulated dose -- data['SDE']
    data = data.copy()
    SSs = pd.unique(data.SS)
    data['SDE'] = np.nan
    data['DDE'] = np.nan
    data['LDE'] = np.nan
    data['dSDE'] = np.nan
    data['dDDE'] = np.nan
    data['dLDE'] = np.nan
    data['EnergyEst'] = np.nan
    data['Rad_Quality'] = np.nan
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]]
    #~
    for PC in PCs: data['CV_'+PC] = np.nan
    if (len(SSs) == 1) & (numpy.isnan(SSs[0])): 
        return data
    else:
        SSs = SSs[~numpy.isnan(SSs)]
    PC_data=data[PCs].copy()
    #~
    for i, sstate in enumerate(SSs):
        sample = data[data.SS == SSs[i]]
        #if it's not the first steady state, get previous steady state
        if (i == 0):
            if (pCVs.isnull().any()): prev_samp = sample
            else: prev_samp = pCVs.to_frame().T
            if pd.isnull(prev_SDE): prev_SDE = 0
            if pd.isnull(prev_DDE): prev_DDE = 0
            if pd.isnull(prev_LDE): prev_LDE = 0
        else:
            prev_samp = data[data.SS == SSs[i-1]]
            prev_SDE = data[data.SS == SSs[i-1]].SDE.values[0]
            prev_DDE = data[data.SS == SSs[i-1]].DDE.values[0]
            prev_LDE = data[data.SS == SSs[i-1]].LDE.values[0]
        #~
        #set CVs for ss
        for PC in PCs:
            data.loc[sample.index.tolist(), 'CV_' + PC] = np.mean(sample[PC].iloc[:5])
        #~
        #cvs is CVs current - CVs prev    
        cvs = np.mean(sample[PCs].iloc[:5]) - np.mean(prev_samp[PCs].iloc[:5])
        #~
        da_output = pd.Series(get_dose(cvs, DAversion))
        if (da_output[0] < MRD) or (da_output[:4]<0).any() or pd.isnull(da_output[:3]).any(): #lower than MRD or negative energy
            data.loc[sample.index.tolist(), 'SDE'] = prev_SDE          
            data.loc[sample.index.tolist(), 'dSDE'] = 0
            #~
            data.loc[sample.index.tolist(), 'DDE'] = prev_DDE        
            data.loc[sample.index.tolist(), 'dDDE'] = 0
            #~
            data.loc[sample.index.tolist(), 'LDE'] = prev_LDE         
            data.loc[sample.index.tolist(), 'dLDE'] = 0
            #~
            for PC in PCs: 
                data.loc[sample.index.tolist(), PC] = np.mean(prev_samp[PC].iloc[:5])
                data.loc[sample.index.tolist(), 'CV_' + PC] = np.mean(prev_samp[PC].iloc[:5])
        else:
            #set dose with dose algorithm
            data.loc[sample.index.tolist(), 'SDE'] = prev_SDE + da_output[0]          
            data.loc[sample.index.tolist(), 'dSDE'] = da_output[0]
            #~
            data.loc[sample.index.tolist(), 'DDE'] = prev_DDE + da_output[1]          
            data.loc[sample.index.tolist(), 'dDDE'] = da_output[1]
            #~
            data.loc[sample.index.tolist(), 'LDE'] = prev_LDE + da_output[2]          
            data.loc[sample.index.tolist(), 'dLDE'] = da_output[2]
            data.loc[sample.index.tolist(), 'EnergyEst'] = da_output[3]
            data.loc[sample.index.tolist(), 'Rad_Quality'] = da_output[4]
    #~
    data['type']='dose_equiv'
    data[PCs]=PC_data
    #~
    if verbose: print('Dose Calculation: Completed', end = dash)
    return data

#~
#--------------------------------------------------
def get_dose(cvs, version):
            CV2 = cvs[0]
            CV4 = cvs[1]
            CV5 = cvs[2]
            CV6 = cvs[3]
            SDE, DDE, LDE, EnergyEst, Rad_Quality = dose_algorithm(CV2, CV4, CV5, CV6, version)
            return SDE, DDE, LDE, EnergyEst, Rad_Quality
