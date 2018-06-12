#--------------------------------------------------
# dose_algorithm_v1.3
#--------------------------------------------------
version='v1.3'

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

##
def dose_algorithm(CV2, CV4, CV5, CV6, Mversion = False, verbose = False, debug = False):
    if Mversion==version:
        # --------------------------------------------------------------------------
        # Initialize CVs array
        # --------------------------------------------------------------------------
        CV = np.array([CV2, CV4, CV5, CV6])
        CV[CV < 5] = 5.0 # Set lower limit of 5
        #~
        # Calculate ratios Rxy=PCx/PCy
        R42 = CV[1]/CV[0]
        R26 = CV[0]/CV[3]
        R54 = CV[2]/CV[1]
        R46 = CV[1]/CV[3]
        #~
        Rs = np.array([R42, R26, R54, R46])
        Rks = np.array([R26, R54, R46])
        Rs[Rs < 1] = 1.0
        Rs[Rs > 7] = 7.0
        #~
        avg_R = np.mean(Rs)
        std_R = np.std(Rs)
        avg_Rk = np.mean(Rks)
        std_Rk = np.std(Rks)
        #~
        k = (1 - avg_Rk)**2 + std_Rk**2 
        #~
        a = (avg_R < 1.08) and (std_R < 0.08)
        b = (k < 0.1) and (R26 < 1.09)
        
        # --------------------------------------------------------------------------
        # Calculate estimated energy
        # --------------------------------------------------------------------------
        a0 = -33.1854095397879
        a1 = 58.8226964608858
        a2 = -7.61988321985791
        a3 = 0.41739199730716
        #~
        if a or b or all(CV<50): EnergyEst = 662.0 # high energy branch
        elif R42 >= 4: EnergyEst = 20.0 # low energy branch
        else: 
            EnergyEst = (a0 
                        + a1/np.log(R26) 
                        + a2/np.log(R26)**2 
                        + a3/np.log(R26)**3)
        
        # --------------------------------------------------------------------------
        # Calculate shallow dose equivalent - Hp07 
        # --------------------------------------------------------------------------
        b0 = 0.855696987371797
        b1 = 2011.9387213917
        #~
        c0 = 0.891705761
        c1 = 97.6618458
        c2 = -11886.4543
        c3 = 1591065.12
        c4 = -72991770.2
        c5 = 1390833240
        c6 = -9655238080
        #~
        # Calculate Dose Conversion Factor for PC4 (DCF_4)
        if EnergyEst > 600: DCF_4 = 1.0
        elif EnergyEst < 25: DCF_4 = 3.0
        elif EnergyEst > 49: DCF_4 = b0 + b1*np.log(EnergyEst)/EnergyEst**2
        else: 
            DCF_4 = (c0 
                    + c1/EnergyEst 
                    + c2/EnergyEst**2 
                    + c3/EnergyEst**3 
                    + c4/EnergyEst**4 
                    + c5/EnergyEst**5 
                    + c6/EnergyEst**6)
        #~
        SDE = CV4/DCF_4
        
        # --------------------------------------------------------------------------
        # Calculate deep dose equivalent - Hp10 
        # --------------------------------------------------------------------------
        d1 = -4.22431326458354
        d2 = 2.0079788183708
        d3 = -0.293179726787833
        d4 = 0.0206839475758888
        d5 = -0.000706999550075449
        d6 = 0.000009340577820916
        #~
        # Compute ratio of Hp10 and Hp07 (DS_Ratio)
        if EnergyEst > 150: DS_Ratio = 1.0
        else:
            DS_Ratio = (d1 
                        + d2*np.sqrt(EnergyEst) 
                        + d3*EnergyEst 
                        + d4*EnergyEst*np.sqrt(EnergyEst) 
                        + d5*EnergyEst**2 
                        + d6*EnergyEst**2.5)
        #~
        DDE = SDE*DS_Ratio
        
        # --------------------------------------------------------------------------
        # Calculate low dose equivalent - Hp03 
        # --------------------------------------------------------------------------
        e0 = 20.1522589953869
        e1 = -632.326790265013
        e2 = 8586.52813821031
        e3 = -60922.3250230036
        e4 = 230413.891596824
        e5 = -350814.390424187
        e6 = -574298.883693541
        e7 = 3583582.68747921
        e8 = -6717525.69467777
        e9 = 5924810.442887
        e10 = -2076795.7291245
        LEE = np.log(EnergyEst)
        #~
        # Compute ratio of Hp03 and Hp07 (LS_Ratio)
        LS_Ratio = (e0 
                    + e1/LEE 
                    + e2/LEE**2 
                    + e3/LEE**3 
                    + e4/LEE**4 
                    + e5/LEE**5 
                    + e6/LEE**6 
                    + e7/LEE**7 
                    + e8/LEE**8 
                    + e9/LEE**9 
                    + e10/LEE**10)
        #~
        LDE = SDE*LS_Ratio
        
        #---------------------------------------------------------------------------
        # Dose calculation modification for accident M150 x-ray exposures
        #---------------------------------------------------------------------------
        if (CV[0] > 100000) and (R26 > 1.3):
            EnergyEst = 73.0
            SDE = CV[3]/2
            DDE = SDE*1.09
            LDE = SDE*1.00
        
        #---------------------------------------------------------------------------
        # Radiation Quality Determination
        #---------------------------------------------------------------------------
        Min_Energy_Dose = 30
        if all(CV < Min_Energy_Dose): Rad_Quality = 'PH' 
        elif EnergyEst < 40: Rad_Quality = 'PL'
        elif EnergyEst >= 40 and EnergyEst < 150: Rad_Quality = 'PM'
        else : Rad_Quality = 'PH'
        return  SDE, DDE, LDE, EnergyEst, Rad_Quality
    else:
        data=pd.DataFrame()
        print(dash+'Error: Wrong Version Number',end=dash)
        print('Module version: '+ str(version) + '\nProvided version: ' + str(Mversion),end=dash)
        return data
