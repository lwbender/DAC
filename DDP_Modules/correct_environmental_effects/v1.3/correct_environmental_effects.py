#--------------------------------------------------
# correct_environmental_effects_v1.3
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
def correct_environmental_effects(data, Ks, As, Bs, Cs, abST, verbose = False, debug = False):
    #~
    if verbose: print(dash+'Temperature Correction: Initialized',end=dash)
    #~
    PCs = ['PC{}'.format(k) for k in [2,4,5,6]] #PC1-PC7
    PCi=(data.index-abST).total_seconds()
    PCt=data.temp_c #temp in C (y model)
    data=data.copy()


    def env_model(PCm,K,A,B,C):
        (PCt,PCi,PCx)=PCm
        return PCx-(K*PCt+(A/100)*(1+PCi)**(B/10000))+C 

    
    for i,PC in enumerate(PCs):
        PCx=data[PC]
        TC_PCx=env_model((PCt,PCi,PCx),Ks[PC],As[PC],Bs[PC],Cs[PC]) 
        data['K_'+PC]=Ks[PC]
        data['A_'+PC]=As[PC]
        data['B_'+PC]=Bs[PC]
        data['C_'+PC]=Cs[PC]
        data.loc[:,PC]=TC_PCx    
    #~
    if verbose: print('Temperature Correction: Completed',end=dash)
    data['Mversion']='v1.3'
    #~
    return data
