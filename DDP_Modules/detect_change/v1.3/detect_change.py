#--------------------------------------------------
# detect_change_v1.3
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
def detect_change(data, change_detection_factor = None, verbose = False, debug = False):
    #~
    if verbose: print(dash+'Change Detection: Initialized',end=dash)
    #~
    #standard definitions
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC2...PC6
    PCVs = ['PC{}_var'.format(k) for k in [2,4,5,6]] #PC2_var...PC6_var
    PCCs = ['PC{}_cluster'.format(k) for k in [2,4,5,6]] #PC2_clusters...PC6_clusters
    PCDs = ['PC{}_dose'.format(k) for k in [2,4,5,6]] #PC2_dose...PC6_dose
    #~
    if verbose: print('Clusters Found: ')
    for i, PC in enumerate(PCs):
        #find clusters in dose for each Pcap
        data[PCCs[i]], data[PCDs[i]] = change_detector(data = data[PCs[i]], data_var = data[PCVs[i]], 
                                                    threshold = change_detection_factor[PCs[i]], verbose = verbose)
        data[PC+'_CDF']=change_detection_factor[PCs[i]]
        if verbose: print(PCs[i] + ': ' + str(data[PCCs[i]].unique()[-1]))
    #~
    if verbose: print('Change Detection: Completed',end=dash)
    #~
    data['Mversion']='v1.3'
    return data


##
def change_detector(data, data_var, threshold = None, verbose = False, debug = False):
    if verbose: print('Detecting steps in dose for '+ data.name+'...')
    #~
    #process on a copy of the data
    dose=data.copy()
    data=data.copy()
    variance = data_var.copy()
    cluster = data.copy()
    #~
    count = 1
    if not threshold:
        threshold = 1000
    #~
    for i, x in enumerate(dose):
        #~
        #intialize with first dose value and variance
        if i == 0: 
            x0 = x #previous estimation 
            x_var0 = variance.iloc[i] # previous estimation variance
            idx = i #index for beginning of cluster
        #~
        #after the first value....
        else:
            x_var = variance.iloc[i]
            #~
            #calculate joint probability
            [g_x, g_var] = gauss_multiply([x0, x_var0], [x, x_var])
            #~
            #calculate t-statistic 
            t = ((x-x0)**2.)/g_var
            #~
            n = i-idx

            #if above threshold, change detected, replace previous static portion with mean of the second half of the cluster
            if t > threshold**2:
                x0=x
                idx = i #reset index for beginning of cluster
                count += 1 #add to cluster count
            #~
            #if below threshold, keep measurement value but update variance with joint variance
            else:
                dose.iloc[i] = numpy.mean(data.iloc[i-round(.5*n)-1:i])
                variance.iloc[i] = g_var
            #~
            #update the previous measurement vaeiance
            x_var0 = variance.iloc[i]
        #~
        #add cluster index
        cluster.iloc[i] = count   
    #~
    return cluster, dose  
    
##
def gauss_multiply(g1, g2):
    #~
    #extract gauss parameters
    mu1, var1 = g1
    mu2, var2 = g2
    #~
    #determine new gauss parameters
    mean = (var1*mu2 + var2*mu1) / (var1 + var2)
    variance = (var1 * var2) / (var1 + var2)
    #~
    return [mean, variance]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gauss_add(g1, g2):
    #~
    #extract gauss parameters
    mu1, var1 = g1
    mu2, var2 = g2
    #~
    #determine new gauss parameters
    mean = mu1 + mu2
    variance = var1 + var2
    #~
    return [mean, variance]