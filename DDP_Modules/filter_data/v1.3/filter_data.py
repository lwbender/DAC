#--------------------------------------------------
# filter_data_v1.3
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
def filter_data( data, var_BAs = None, var_Bs = None, dx=0., dx_var=0., var_0= pd.Series(), verbose = False, debug = False):
    #~
    data=data.copy()
    if verbose: print(dash+'Dose Filteration: Initialized',end=dash)
    #~
    cols=['PC{}'.format(k) for k in [2,4,5,6]] #PC1-PC7
    #~
    for col in cols:
        # handle default conditions
        temp=data[col]
        xs=numpy.zeros(len(temp))
        x_vars=numpy.zeros(len(temp))
        xs[0:2] = numpy.mean(temp[0:2])
        if (len(var_0)!=4):
            x_vars[0:2] = numpy.var(temp[0:2])
        else:
            x_vars[0:2] = var_0[col]
            
        var_ba = var_BAs[col]
        var_b = var_Bs[col]

        #~
        for i,z in enumerate(temp):
            if i<2: continue
            #previous
            xp=xs[i-1]
            xp_var=x_vars[i-1]
            #current
            xc=z
            xc_var=var_ba
            wf=var_b #weighting factor
            #add prediction
            xp,xp_var = gauss_add([xp,xp_var], [dx,dx_var]) 
            #joint prediction
            xj,xj_var = gauss_multiply([xp,xp_var], [xc,xc_var])
            #scatter var
            s_var = ((xc - xj)**4) / wf
            w_var=xj_var+s_var #weighted var
            #
            #update current value
            xs[i]=xj
            x_vars[i]=w_var
        #~
        data[col]=xs
        data[col+'_var']=x_vars
        #~
        data[col+'_VBA']=var_ba
        data[col+'_VB']=var_b
        #~
    if verbose: print('Dose Filteration: Completed',end=dash)
    #~
    data['Mversion']='v1.3'
    return data

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