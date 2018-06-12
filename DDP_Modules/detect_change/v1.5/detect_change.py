#--------------------------------------------------
# detect_change_v1.5
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
def detect_change(data, pCDEs, pCDVs, CDFs, verbose = False, debug = False):
    if verbose: print('Change Detection: Initialized', end = dash)
    #~
    data=data.copy()
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC2,4,5,6
    FVs = ['FV_PC{}'.format(k) for k in [2,4,5,6]] #FV_PC2,4,5,6
    ciPCs = ['CI_PC{}'.format(k) for k in [2,4,5,6]] #ciPC2,4,5,6
    CDEs = ['CDE_PC{}'.format(k) for k in [2,4,5,6]] #CDE_PC2,4,5,6
    CDVs = ['CDV_PC{}'.format(k) for k in [2,4,5,6]] #CDV_PC2,4,5,6
    #~
    if verbose: print('Clusters Found: ')
    for i, PC in enumerate(PCs):
        data[ciPCs[i]], data[CDEs[i]], data[CDVs[i]] = change_detector(data[PCs[i]], data[FVs[i]], pCDEs[PCs[i]], pCDVs[PCs[i]], CDFs[PCs[i]], verbose, debug)
        if verbose: print(PCs[i] + ': ' + str(data[ciPCs[i]].unique()[-1]))
    #~
    data['type']='cluster'
    #~
    if verbose: print(dash[1:] + 'Change Detection: Completed', end = dash)
    return data

#~
#--------------------------------------------------
def change_detector(data, data_var, px, pxvar, threshold, verbose = False, debug = False):
    #--------------------------------------------------
    #Change Detection Initialization
    #--------------------------------------------------
    data = data.copy()
    CDE = data.copy()
    CDV = data_var.copy()
    cluster_index = data.copy()
    idx = 1
    #--------------------------------------------------
    #Previous Measurement Values
    if pd.isnull(px): xp = data.iloc[0]
    else: xp = px
    #~
    if pd.isnull(pxvar): xp_var = CDV.iloc[0]
    else: xp_var = pxvar
    #--------------------------------------------------
    #Run Change Detection
    for i, z in enumerate(data):
        #current measurement values
        xc = z
        xc_var = CDV.iloc[i]
        #calculate joint probability
        [xj, xj_var] = gauss_multiply([xp, xp_var], [xc, xc_var])
        #~
        #calculate t-statistic 
        t = ((xc - xp)**2.)/xj_var
        #~
        if t > threshold**2: #change detected
            xp = xc # set new baseline at current measurement
            idx += 1 #add to cluster count
        else: 
            CDV.iloc[i] = xj_var #update variance
        xp_var = CDV.iloc[i]
        #~
        CDE.iloc[i] = xp
        cluster_index.iloc[i] = idx   
    #~
    return cluster_index, CDE, CDV  

#~
#--------------------------------------------------
def gauss_multiply(g1, g2):
    #extract gauss parameters
    mu1, var1 = g1
    mu2, var2 = g2
    #~
    #determine new gauss parameters
    mean = (var1*mu2 + var2*mu1) / (var1 + var2)
    variance = (var1 * var2) / (var1 + var2)
    #~
    return [mean, variance]

#~
#--------------------------------------------------
def gauss_add(g1, g2):
    #extract gauss parameters
    mu1, var1 = g1
    mu2, var2 = g2
    #~
    #determine new gauss parameters
    mean = mu1 + mu2
    variance = var1 + var2
    #~
    return [mean, variance]