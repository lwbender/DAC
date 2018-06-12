#--------------------------------------------------
# import_data_v1.7
#--------------------------------------------------
#~
#--------------------------------------------------
# Standard imports & definitions
import os
import sys
import getpass 
import pymssql 
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
qry = ''
with open('DDP_Modules/sql_queries/alpha_rm_query.sql', 'r') as f_sql:
            for rw in f_sql:
                rw = rw.rstrip('\n')
                rw = ' '.join(rw.split())
                #
                qry +=  ' ' + rw + ' '
f_sql.close()
qry1 = qry + ' and ('
#~
qry = ''
with open('DDP_Modules/sql_queries/configDB_query.sql', 'r') as f_sql:
            for rw in f_sql:
                rw = rw.rstrip('\n')
                rw = ' '.join(rw.split())
                #
                qry +=  ' ' + rw + ' '
f_sql.close()
qry3 = qry + ' where ('

#~
#--------------------------------------------------
def import_data(dosimeter_ids, SQL_cons = None, verbose = False, debug = False):
    if verbose: print('Data Importation: Initialized', end = dash)      
    #~
    if SQL_cons == None: SQL_cons = start_SQL_connection()
    #~
    #--------------------------------------------------
    # Generate & Execute SQL Queries and Process Raw Data
    #--------------------------------------------------
    #get data from alpha
    qrys = get_qrys(dosimeter_ids)
    data = process_qry(qrys[0], SQL_cons[0])
    configDB = get_configDB(qrys[1], SQL_cons[1])
    #~
    #combine data
    data = data.sort_values(by = ['dos_ID', 'mTS'])
    #~
    #data = data.drop(['mTS'], axis = 1)
    data = data.drop(['mTS','PC2','T_Int','T_Ext'], axis = 1)
    data['type'] = 'raw'
    #~
    #formatting data and removing duplicates
    data = data.drop_duplicates()
    #~
    if verbose: print('Data Importation: Completed', end = dash)
    return data, configDB, SQL_cons

#~
#--------------------------------------------------
def start_SQL_connection(**kwargs):
    con_alpha = get_alpha_SQL(**kwargs)
    #~
    con_configDB = get_configDB_SQL(**kwargs)
    #~
    return con_alpha, con_configDB

#~
#--------------------------------------------------
def get_alpha_SQL(type='notebook',**kwargs):
    #~
    if type=='notebook':
        db_name   = 'vfdb_b01'
        db_server = 'lobdb001.ldrtest2.landauerinc.com'
        db_domain = 'LANDAUER' #not used
        user_id = 'Verifii_AlphaDB'
        passwd = 'mZ0y$^gXtUK!'
    else: 
        db_name   = kwargs['SQL_DBname']
        db_server = kwargs['SQL_servername']
        db_domain = 'LANDAUER' #not used
        user_id = kwargs['SQL_username']
        passwd = kwargs['SQL_password']
        #~
    print('Alpha SQL connection-')
    print('Server: {} '.format(db_server))
    print('Database: {} '.format(db_name))
    print('Domain: {} '.format(db_domain))
    print('User ID: {} '.format(user_id))
    print('Password: {} '.format('*****'))
    #~
    connect_data = {'user' : user_id,
                    'server' : db_server,
                    'database' : db_name,
                    'password' : passwd
                    }
    con_alpha = pymssql.connect(**connect_data)
    print(end = dash[1:])
    #~
    return con_alpha
    
#~
#--------------------------------------------------
def get_configDB_SQL(type='notebook',**kwargs):
    #~
    if type=='notebook':
        db_name   = 'vfsc_q01'
        db_server = 'LOQDB210.int.landauerinc.com'
        db_domain = 'LANDAUER' #not used
        user_id = 'vfsc_q01_rw'
        passwd = 'HjBMh@psZop5'
    else: 
        db_name   = kwargs['coeffDB_DBname']
        db_server = kwargs['coeffDB_servername']
        db_domain = 'LANDAUER' #not used
        user_id = kwargs['coeffDB_username']
        passwd = kwargs['coeffDB_password']
    #~
    print('ConfigDB SQL connection-')
    print('Server: {} '.format(db_server))
    print('Database: {} '.format(db_name))
    print('Domain: {} '.format(db_domain))
    print('User ID: {} '.format(user_id))
    print('Password: {} '.format('*****'))
    #~
    connect_data = {'user' : user_id,
                    'server' : db_server,
                    'database' : db_name,
                    'password' : passwd
                    }
    con_configDB = pymssql.connect(**connect_data)
    con_configDB.autocommit(True)
    print(end = dash[1:])
    #~
    return con_configDB

#~
#--------------------------------------------------
def get_qrys(dos_IDs):
    RM_qry = get_alpha_qry(dos_IDs)
    configDB_qry = get_configDB_qry(dos_IDs)
    #~
    return (RM_qry, configDB_qry)   
    
#~
#--------------------------------------------------
def get_alpha_qry(dos_IDs):
    dos_str = ''
    for dos_ID in dos_IDs: dos_str += "(d.SerialNumber = '" + str(dos_ID) + "')" + " or "
    dos_str = dos_str[:-4]
    RM_qry = qry1 + dos_str + ')'
    return RM_qry  

#~
#--------------------------------------------------
def get_configDB_qry(dos_IDs):
    dos_str = ''
    for dos_ID in dos_IDs: dos_str += "(c.DosimeterSerialNumber = '" + str(dos_ID) + "')" + " or "
    dos_str = dos_str[:-4]
    configDB_qry = qry3 + dos_str + ')'
    #~
    return configDB_qry
    
#~
#--------------------------------------------------
def process_qry(qry, SQL_con):
    #~
    #initialize server and execute query
    csr = SQL_con.cursor()
    csr.execute(qry)
    #~
    #extract and match column labels
    col_map = { 
                'dosimeterid' : 'dos_ID',
                'measurementid' : 'mID',
                'measurementtimestamp' : 'mTS',
                'c39' : 'PC1',
                'c40' : 'PC2',
                'c41' : 'PC3',
                'c42' : 'PC4',
                'c43' : 'PC5', 
                'c44' : 'PC6', 
                'c46' : 'PC7', 
                'tempint' : 'T_Int',
                'tempext' : 'T_Ext',
                'motiondetectioncount' : 'TCPM'
              }
    cols = [col_map.get(rw[0],rw[0]) for rw in csr.description]
    #~
    #fetch from SQL database and store in pandas DataFrame
    data = pandas.DataFrame(csr.fetchall(), index = None, columns = cols)
    #~
    #make timestamp the index and sort 
    data.index = data['mTS'].astype('datetime64[ns]')
    #~
    #store analysis parameters
    PCs = ['PC{}'.format(k) for k in range(1,8)] #PC1-PC7
    RDC = ['T_Int','T_Ext']
    data[PCs + RDC] = data[PCs + RDC].astype(np.float64) #change PCs to float
    data['mID'] = data['mID'].astype(np.int) #change PCs to float
    #~
    return data  
    
#~
#--------------------------------------------------
def get_configDB(qry, SQL_con):
    #~
    #initialize server and execute query
    csr = SQL_con.cursor()
    csr.execute(qry)
    cols = [rw[0] for rw in csr.description]
    #~
    configDB = pandas.DataFrame(csr.fetchall(), index = None, columns = cols)
    #~
    configDB['dos_ID'] = configDB.DosimeterSerialNumber
    configDB = configDB.drop(['DosimeterSerialNumber', 'DosimeterDoseCalcCoefficientID', 'Active'], axis = 1)
    Ks = ['K_PC{}'.format(k) for k in [2, 4, 5, 6]]
    As = ['A_PC{}'.format(k) for k in [2, 4, 5, 6]]
    Bs = ['B_PC{}'.format(k) for k in [2, 4, 5, 6]]
    Cs = ['C_PC{}'.format(k) for k in [2, 4, 5, 6]]
    Ss = ['S_PC{}'.format(k) for k in [2, 4, 5, 6]]
    configDB[Ks + As + Bs + Cs + Ss] = configDB[Ks + As + Bs + Cs + Ss].astype(np.float64) #change PCs to float
    #~
    return configDB