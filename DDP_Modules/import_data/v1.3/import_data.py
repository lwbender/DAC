#--------------------------------------------------
# import_data_v1.3
#--------------------------------------------------

## Standard imports & definitions
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

##
def import_data( dosimeter_id, start_date = None, end_date = None, SQL_con = None, type = 'notebook', 
Pversion=False, verbose = False, debug = False):
    #~
    if verbose: print(dash + 'DDPsp: Querying database', end = dash)      
    #~
    if type == 'notebook':
        #initiate SQL connections if none
        if SQL_con == None: SQL_con = start_SQL_connection()
        #~
        #get data from alpha
        qrys = get_alpha_qry(dosimeter_id, start_date, end_date)
        data1 = process_qry(qrys[0], SQL_con[1])
        data2 = process_qry(qrys[1], SQL_con[1])
        #~
        #get data from QA
        #qry = get_QA_qry(dosimeter_id, start_date, end_date)
        #data3 = process_qry(qry, SQL_con[0]) 
        #~
        #combine data from different databases
        data = data2.append(data1).sort_index()
        #~
        #formatting data and removing duplicates
        PCs = ['PC{}'.format(k) for k in range(1,8)] #PC1-PC7
        RDC = ['T_Int','T_Ext']
        data[PCs+RDC] = data[PCs+RDC].astype(np.float64) #change PCs to float
        data=data.drop_duplicates()
    #~
    elif type == 'script':
        #initiate SQL connections if none
        if SQL_con == None: SQL_con = get_alpha_SQL()    
        #-------------------------------------
        #get data from alpha
        qrys = get_alpha_qry(dosimeter_id, start_date, end_date)
        data1 = process_qry(qrys[0], SQL_con)
        data2 = process_qry(qrys[1], SQL_con)
        #combine data from different databases
        data = data2.append(data1).sort_index()
        #~
        #formatting data and removing duplicates
        PCs = ['PC{}'.format(k) for k in range(1,8)] #PC1-PC7
        data[PCs] = data[PCs].astype(np.float64) #change PCs to float
        data=data.drop_duplicates()
    #~
    if verbose: print('DDPsp: Data loaded',end=dash)
    #~
    data['Pversion']=Pversion
    data['Mversion']='v1.3'
    return data, SQL_con
    
##    
    
def get_alpha_SQL(SQL_username, SQL_password, SQL_servername, SQL_DBname):
    #~
    print('Server: {} '.format(SQL_servername))
    print('Database: {} '.format(SQL_DBname))
    print('User ID: {} '.format(SQL_username))
    print('Password: {} '.format('*****'))
    #~
    connect_data = {'user': SQL_username, 
    'server': SQL_servername, 
    'database': SQL_DBname, 
    'password': SQL_password}
    con_alpha = pymssql.connect(**connect_data)
    #~
    return con_alpha
    
##
def get_QA_qry(dosimeter_id, start_date, end_date):
    #~
    #labels for columns that will be extracted
    col_map = { 
                'c39' : 'PC1',
                'c40' : 'PC2',
                'c41' : 'PC3',
                'c42' : 'PC4',
                'c43' : 'PC5', 
                'c44' : 'PC6', 
                'c46' : 'PC7', 
                'measurementtimestamp' : 'timestamp',
                'tempint' : 'T_Int',
                'tempext' : 'T_Ext'
              }
    #~
    #generate column id list in string format
    col_ids = ', '.join(['%s' % (x) for x,y in col_map.items()])
    #~
    #build sql query for QA database
    qry = 'select {col} from fieldtrialmeasurements where dosimeterid=\'{id}\' '.format(col = col_ids, id = dosimeter_id)
    if not start_date is None: qry = qry + ' and measurementtimestamp>=\'{}\' '.format(start_date)
    if not end_date   is None: qry = qry + ' and measurementtimestamp<=\'{}\' '.format(end_date)
    #~
    return (qry, dosimeter_id, start_date, end_date)
    
##
# def start_SQL_connection():
#     print(dash+'Starting SQL connections',end=dash)
#     #~
#     #get QA connection
#     con_QA=get_QA_mssql()
#     #~
#     # test connection
#     csr=con_QA.cursor()
#     csr.execute('select count(*) from fieldtrialmeasurements where dosimeterid=\'44AC1854BACE\'')
#     #~
#     #if successful:
#     if csr.fetchone()[0]==9120: 
#         print(dash[1:]+'QA database connection established',end=dash)
#         #~
#         #get alpha connection
#         con_alpha=get_alpha_mssql()
#         print(dash[1:]+'Alpha database connection established',end=dash)
#     #~
#     #if error:
#     else: print(dash[1:]+'Fatal database connection error',end=dash)
#     return (con_QA,con_alpha)
    
    
    
def start_SQL_connection():
    print(dash+'Starting SQL connections',end=dash)
    #~
    #get QA connection
    #con_QA=get_QA_mssql()
    #~
    # test connection
    #csr=con_QA.cursor()
    #csr.execute('select count(*) from fieldtrialmeasurements where dosimeterid=\'44AC1854BACE\'')
    #~
    con_alpha=get_alpha_mssql()
    con_QA=None
    #if successful:
    # if csr.fetchone()[0]==9120: 
    #     print(dash[1:]+'QA database connection established',end=dash)
    #     #~
    #     #get alpha connection
    #     con_alpha=get_alpha_mssql()
    #     print(dash[1:]+'Alpha database connection established',end=dash)
    # #~
    #if error:
    #else: print(dash[1:]+'Fatal database connection error',end=dash)
    return (con_QA,con_alpha)

##
def get_QA_mssql():
    #~
    db_name   = 'vedb_t01'
    db_server = 'loqdb240.int.landauerinc.com'
    db_domain = 'LANDAUER'
    user_id = '{}\\{}'.format(db_domain, getpass.getuser())
    #~
    print('Server: {} '.format(db_server))
    print('Database: {} '.format(db_name))
    print('Domain: {} '.format(db_domain))
    print('User ID: {} '.format(user_id[len(db_domain)+1:]))
    #~
    passwd = getpass.getpass('Password: ')
    #~
    connect_data = {'user':user_id, 'server':db_server, 'database':db_name, 'password':passwd}
    con_QA = pymssql.connect(**connect_data)
    #~
    return con_QA
    
##
def get_alpha_mssql():
    #~
    db_name   = 'vfdb_b01'
    db_server = 'lobdb001.ldrtest2.landauerinc.com'
    db_domain = 'LANDAUER' #not used
    user_id = 'Verifii_AlphaDB'
    passwd = 'mZ0y$^gXtUK!'
    #~
    print('Server: {} '.format(db_server))
    print('Database: {} '.format(db_name))
    print('Domain: {} '.format(db_domain))
    print('User ID: {} '.format(user_id))
    print('Password: {} '.format('*****'))
    #~
    connect_data = {'user':user_id, 'server':db_server, 'database':db_name, 'password':passwd}
    con_alpha = pymssql.connect(**connect_data)
    #~
    return con_alpha
    
##
def get_alpha_qry(dosimeter_id,start_date,end_date):
    #~
    #labels for columns that will be extracted
    select_map = { 
                    'c39' : 'rmv2.Amount',
                    'c40' : 'rmv3.Amount',
                    'c41' : 'rmv4.Amount',
                    'c42' : 'rmv5.Amount',
                    'c43' : 'rmv6.Amount', 
                    'c44' : 'rmv7.Amount', 
                    'c46' : 'rmv8.Amount', 
                    'tempint' : 'rm.InternalTemp',
                    'tempext' : 'rm.ExternalTemp',
                    'measurementtimestamp' : 'rm.MeasurementDate',
                    'motiondetectioncount' : 'rm.MotionDetectionCounter'
                 }
    #~
    select_str = ', '.join([ x + ' = ' + y for x, y in select_map.items()])
    #~
    db_map = [ 
                ['RawMeasurement', 'rm'],
                ['Dosimeters' , 'd'],
                ['RawMeasurementValues' , 'rmv1'],
                ['RawMeasurementValues' , 'rmv2'], 
                ['RawMeasurementValues' , 'rmv3'], 
                ['RawMeasurementValues' , 'rmv4'], 
                ['RawMeasurementValues' , 'rmv5'],
                ['RawMeasurementValues' , 'rmv6'], 
                ['RawMeasurementValues' , 'rmv7'], 
                ['RawMeasurementValues' , 'rmv8']
             ]
    #~
    db_str = ', '.join([ x + ' as ' + y for x, y in db_map])
    #~
    conditions_map = [ 
                        ['d.DosimeterID' , 'rm.DosimeterID'],
                        ['rmv1.RawMeasurementID', 'rm.RawMeasurementID'],
                        ['rmv2.RawMeasurementID', 'rm.RawMeasurementID'], 
                        ['rmv3.RawMeasurementID', 'rm.RawMeasurementID'], 
                        ['rmv4.RawMeasurementID', 'rm.RawMeasurementID'], 
                        ['rmv5.RawMeasurementID', 'rm.RawMeasurementID'],
                        ['rmv6.RawMeasurementID', 'rm.RawMeasurementID'], 
                        ['rmv7.RawMeasurementID', 'rm.RawMeasurementID'], 
                        ['rmv8.RawMeasurementID', 'rm.RawMeasurementID'], 
                        ['rmv1.SensorTypeID', '1'],
                        ['rmv2.SensorTypeID', '2'], 
                        ['rmv3.SensorTypeID', '3'], 
                        ['rmv4.SensorTypeID', '4'], 
                        ['rmv5.SensorTypeID', '5'],
                        ['rmv6.SensorTypeID', '6'], 
                        ['rmv7.SensorTypeID', '7'], 
                        ['rmv8.SensorTypeID', '8'], 
                        ['d.SerialNumber', "'" + str(dosimeter_id) + "'"]
                     ]
    #~
    conditions_str = ' and '.join([ x + ' = ' + y for x, y in conditions_map])
    #~
    #build sql query for alpha database
    qry = 'select {slc} from {db} where {condition} '.format(slc = select_str, db = db_str, condition = conditions_str)
    if not start_date is None: qry = qry + ' and measurementDate>=\'{}\' '.format(start_date)
    if not end_date   is None: qry = qry + ' and measurementDate<=\'{}\' '.format(end_date)
    qry1 = qry
    #~
    #--------------------------------------------------
    #~
    #labels for columns that will be extracted
    select_map = { 
                    'c39' : 'rmv2.Amount',
                    'c40' : 'rmv3.Amount',
                    'c41' : 'rmv4.Amount',
                    'c42' : 'rmv5.Amount',
                    'c43' : 'rmv6.Amount', 
                    'c44' : 'rmv7.Amount', 
                    'c46' : 'rmv8.Amount',
                    'tempint' : 'drm.InternalTemp',
                    'tempext' : 'drm.ExternalTemp',
                    'measurementtimestamp' : 'drm.MeasurementDate'
                 }
    #~
    select_str = ', '.join([ x + ' = ' + y for x, y in select_map.items()])
    #~
    db_map = [ 
                ['Dosimeters' , 'd'],
                ['DiscardedRawMeasurement', 'drm'],
                ['DiscardedRawMeasurementValues' , 'drmv'],
                ['DiscardedRawMeasurementValues' , 'rmv1'],
                ['DiscardedRawMeasurementValues' , 'rmv2'], 
                ['DiscardedRawMeasurementValues' , 'rmv3'], 
                ['DiscardedRawMeasurementValues' , 'rmv4'], 
                ['DiscardedRawMeasurementValues' , 'rmv5'],
                ['DiscardedRawMeasurementValues' , 'rmv6'], 
                ['DiscardedRawMeasurementValues' , 'rmv7'], 
                ['DiscardedRawMeasurementValues' , 'rmv8']
             ]
    #~
    db_str = ', '.join([ x + ' as ' + y for x, y in db_map])
    #~
    conditions_map = [ 
                        ['drm.DosimeterID' , 'd.DosimeterID'],
                        ['drmv.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'],
                        ['rmv1.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'],
                        ['rmv2.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'], 
                        ['rmv3.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'], 
                        ['rmv4.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'], 
                        ['rmv5.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'],
                        ['rmv6.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'], 
                        ['rmv7.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'], 
                        ['rmv8.DiscardedRawMeasurementID', 'drm.DiscardedRawMeasurementID'], 
                        ['rmv1.SensorTypeID', '1'],
                        ['rmv2.SensorTypeID', '2'], 
                        ['rmv3.SensorTypeID', '3'], 
                        ['rmv4.SensorTypeID', '4'], 
                        ['rmv5.SensorTypeID', '5'],
                        ['rmv6.SensorTypeID', '6'], 
                        ['rmv7.SensorTypeID', '7'], 
                        ['rmv8.SensorTypeID', '8'], 
                        ['d.SerialNumber', "'" + str(dosimeter_id) + "'"] 
                     ]
    #~
    conditions_str = ' and '.join([ x + ' = ' + y for x, y in conditions_map])
    conditions_str =  conditions_str + 'and drm.reason is null'
    #~
    #build sql query for alpha database
    qry = 'select {slc} from {db} where {condition} '.format(slc = select_str, db = db_str, condition = conditions_str)
    if not start_date is None: qry = qry + ' and measurementDate>=\'{}\' '.format(start_date)
    if not end_date   is None: qry = qry + ' and measurementDate<=\'{}\' '.format(end_date)
    qry2 = qry
    #~
    return ((qry1, dosimeter_id, start_date, end_date), (qry2, dosimeter_id, start_date, end_date))   
    
##
def process_qry(qry, SQL_con):
    #~
    #extract query parameters
    dosimeter_id = qry[1]
    start_date = qry[2]
    end_date = qry[3]
    qry = qry[0]
    #~
    #initialize server and execute query
    csr = SQL_con.cursor()
    csr.execute(qry)
    #~
    #extract and match column labels
    col_map = { 
                'c39' : 'PC1',
                'c40' : 'PC2',
                'c41' : 'PC3',
                'c42' : 'PC4',
                'c43' : 'PC5', 
                'c44' : 'PC6', 
                'c46' : 'PC7', 
                'measurementtimestamp' : 'timestamp',
                'tempint' : 'T_Int',
                'tempext' : 'T_Ext',
                'motiondetectioncount' : 'TCPH'
              }
    cols = [col_map.get(rw[0],rw[0]) for rw in csr.description]
    #~
    #fetch from SQL database and store in pandas DataFrame
    data = pandas.DataFrame(csr.fetchall(), index = None, columns = cols)
    #~
    #store analysis parameters
    data['dos_ID'] = dosimeter_id 
    data['start_date'] = start_date
    data['end_date'] = end_date
    #~
    #make timestamp the index and sort 
    data['timestamp'] = data['timestamp'].astype('datetime64[ns]')
    data = data.sort_values(['timestamp'], ascending = [True])
    data.index = data['timestamp']
    del data['timestamp']
    #~
    return data