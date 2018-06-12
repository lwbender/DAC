#--------------------------------------------------
# filter_data_v1.4
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
def filter_data( data,  px, pxvar, var_BAs = None, var_Bs = None, dx=0., dx_var=0., verbose = False, debug = False):
    if verbose: print('Dose Filteration: Initialized', end = dash)
    #~
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC2,4,5,6
    data = data.copy()
    #~
    for PC in PCs:
        #--------------------------------------------------
        #Filter Initialization
        #--------------------------------------------------
        temp = data[PC]
        xs = numpy.zeros(len(temp))
        x_vars = numpy.zeros(len(temp))
        var_ba = var_BAs[PC]
        var_b = var_Bs[PC]
        #--------------------------------------------------
        #Previous Measurement Values
        if (px.isnull().any()): xp = numpy.mean(temp[0:2])
        else: xp = px[PC]
        #~
        if (pxvar.isnull().any()): xp_var = numpy.var(temp[0:2])
        else: xp_var = pxvar[PC]
        #--------------------------------------------------
        #Run Filter
        for i, z in enumerate(temp):
            #current values
            xc = z
            xc_var = var_ba
            wf = var_b #weighting factor
            #~
            #add prediction
            xp, xp_var = gauss_add([xp, xp_var], [dx, dx_var]) 
            #~
            #joint prediction
            xj, xj_var = gauss_multiply([xp, xp_var], [xc, xc_var])
            #~
            #scatter var
            s_var = ((xc - xj)**4) / wf
            w_var = xj_var + s_var #weighted var
            #~
            #update current value
            xs[i] = xj
            x_vars[i] = w_var
            #~
            #update previous value
            xp = xj
            xp_var = w_var
        #--------------------------------------------------
        #Store Values
        data[PC] = xs
        data['FE_' + PC] = xs
        data['FV_' + PC] = x_vars
        #~
        data['VBA_' + PC] = var_ba
        data['VB_' + PC] = var_b
        #~
        data['Mversion'] = 'v1.4'
        data['type'] = 'filtered'
    #~
    if verbose: print('Dose Filteration: Completed', end = dash)
    return data

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