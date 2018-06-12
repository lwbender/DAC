#--------------------------------------------------
# DDP_v1.8
#--------------------------------------------------
version = 'v1.8'
DAversion = 'v1.3'
#--------------------------------------------------
Modules = {'import_data' : 'v1.7',
        'convert_raw_vals' : 'v1.5',
        'correct_environmental_effects' : 'v1.6',
        'filter_data' : 'v1.5',
        'convert_to_dose' : 'v1.5',
        'remove_background_radiation' : 'v1.5',
        'detect_change' : 'v1.5',
        'locate_steady_state' : 'v1.5',
        'run_dose_algorithm' : 'v1.6'
        }
#--------------------------------------------------
import pandas as pd
from os.path import dirname, basename, isfile
import glob
import sys
from importlib import import_module
fn = dirname(__file__)
#--------------------------------------------------
for module in Modules:
    module_dir = fn + '\\DDP_Modules\\' + module + '\\' + Modules[module]
    sys.path.append(module_dir)  
    mod = import_module((module), module)
    globals().update(mod.__dict__)
#--------------------------------------------------
Modules = pd.Series(Modules)[Modules.keys()]
Modules['dose_algorithm'] = DAversion
Modules['Pversion'] = version
Modules = Modules[['Pversion'] + Modules.index[:-1].tolist()]