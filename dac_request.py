#--------------------------------------------------
# DDP_Workbook_v1.7
#--------------------------------------------------
from IPython import get_ipython
#~
#get_ipython().magic('load_ext autoreload')
#get_ipython().magic('autoreload 2')
#get_ipython().magic('matplotlib notebook')
#~
import os
import sys
import numpy
import numpy as np
import pylab as plt
import pandas
import pandas as pd
from datetime import datetime, timedelta
import DDP
import inspect
#~
dash = '\n' + '-'*59 + '\n'
PCs = ['PC{}'.format(k) for k in [3,4,5,6]] 
TPCs = ['TC PC3', 'TC PC4', 'TC PC5', 'TC PC6']
#~

#Gets values from inserted terminal commands
#Takes in a valid command
#Returns either the value that is stated after the command (-cmd a where -cmd is command and a is value)
#Returns null if command doesn't exist, errors if no value for command.
def get_cmd(cmd):
	cmds = ['aET', 'aST', 'uET', 'uST', 'dosIDs', 'fit'] #Valid commands
	if cmd not in cmds:
		print('Command not valid.')
		return
	else:
		if '-' + cmd in sys.argv:
			return sys.argv[sys.argv.index('-' + cmd) + 1]
		else:
			return None
#Replacing datetime.datetime.strptime since it doesn't handle None types 
#Paramters exact same as datetime.datetime.strptime
#Results same as datetime.datetime.strptime but also None if None is given to it
def strptime(string, refstring='%m/%d/%y %H:%M:%S'):
	if string != None:
		try:
			return datetime.strptime(string, refstring)
		except:
			return None
	else:
		return None
		
		
		
try:
	linefit = int(get_cmd('fit'))
except ValueError:
	linefit = 1
		
#Corrects given capacitance values based on temperature
#Inputs a dataframe containing raw data
#Results fitted lines and slopes of the relation
def temp_correct(df_dos):
	global linefite
	#C - C0 = a(Trn^n-T0n^n) + b(...)
	#where Cr = a * Trn^n + b * ...
	#C tries to correct to Cr. 
	#Right now using first T as Tr and therefore correcting to first capacitance value. Fahad uses Tr = 0 which may be a 'safer'
	#Regardless each method results same STDEV.P
	#However which one results a more correct capacitance? Is 'b' the max capacitance of the capacitor when Tr = 0?

	pars = [np.polyfit(df_dos['PC1'], df_dos['PC{0}'.format(i)], linefit) for i in range(3,7)]
	for i, par in enumerate(pars):
		ref_cap = df_dos['PC' + str(i + 3)].iloc[0]
		polyf = np.poly1d(par)
		df_dos['TC PC{0}'.format(i + 3)] =  df_dos['PC' + str(i + 3)] - polyf(df_dos['PC1']) - i * 20 + 80
		df_dos['PCN' + str(i + 3)] = df_dos['PC' + str(i + 3)] - ref_cap - i * 200 + 800
		slopes = []
		
		
	
	return pars

#Handles partial dosimeters IDs passed through the terminal
#Partial is the partial string of a dos ID (can be end bits such as 2980T, 2981R, etc)
#Results in a full dosimeter ID or quits if it's invalid
def handle_dosID(partial):
	id_length = 11
	if 'VA' not in partial:
		if len(partial) >= id_length - 2:
			print('Warning!! Given partial too long')
			return 'VA' + partial[:id_length - 2]
		else:
			return 'VA' + '0' * (id_length - 2 - len(partial)) + partial
	else:
		if len(partial) == id_length:
			return partial
		elif len(partial) > id_length:
			print('Warning!! Given partial too long')
			return 'VA' + partial[:id_length]
		else:
			print('Invalid dosimeter id given.')
			exit()
	
	
#Initializing some formating stuff, printing init info
from matplotlib import dates
date_format = dates.DateFormatter('%m/%d/%y %H:%M:%S')
dc = u'\N{DEGREE SIGN}'
verbose = False
print(dash[1:] + 'DDP_' + DDP.version + ': Module Versions', end = dash)
print(DDP.Modules, end = dash)

#Obtaining whether to use passed or default dosIDs
default_dosIDs = ['VA00002980T','VA00002979C','VA00002981R','VA00002976I']
try:
	dos_IDs = [handle_dosID(s.strip()) for s in get_cmd('dosIDs').split(',')] or default_dosIDs
except:
	dos_IDs = default_dosIDs
	
#Obtaining passed or default start / end datetimes
aST = strptime(get_cmd('aST'))
if aST != None: aST += timedelta(hours=5)
aET = strptime(get_cmd('aET'))
if aET != None: aET += timedelta(hours=5)
if aST == None and aET == None:
	aST = strptime(input('Start Date (mm/dd/yy HH:MM:SS): '))
	if aST != None: aST += timedelta(hours=5)
	aET = strptime(input('End Date (mm/dd/yy HH:MM:SS): '))
	if aET != None: aET += timedelta(hours=5)
fST = aST or strptime(get_cmd('uST')) or datetime.now() - timedelta(days=1) + timedelta(hours=5)
fET = aET or strptime(get_cmd('uET')) or datetime.now() + timedelta(hours=5)

#Opening and passing SQL connection
verbose = True
print(dash[1:] + 'DDP_' + DDP.version + ': Starting SQL connections', end = dash)
SQL_cons = DDP.start_SQL_connection()
SQL_prams = { 
                'dosimeter_ids' : dos_IDs,
                'SQL_cons' : SQL_cons,
                'verbose' : True
            } 
full_data, configDB, SQL_cons = DDP.import_data(**SQL_prams)

#print(list(full_data))

#Refining the raw data to give actual capacitance as well as measurements within the date range
df_doses = [full_data.loc[(full_data.dos_ID == dos_ID) & (full_data.index >= fST) & (full_data.index <= fET)] for dos_ID in dos_IDs]
for df_dos in df_doses:
	for i in range(1, 8):
		if i != 2:
			if i != 7: df_dos['PC{0}'.format(i)] = round(df_dos['PC{0}'.format(i)]/2097152*220000,1) #Rounding to match how SQL would round
			else: df_dos['PC{0}'.format(i)] = round(df_dos['PC{0}'.format(i)]/2097152*220000,2)

			
#Some nasty code for writing out the standard deviation and fitted lines
stdevdf = pd.DataFrame(columns=['Dosimeter ID'] + PCs + TPCs)
eqdf = pd.DataFrame(columns=['Dosimeter ID', 'PC'] + [x for x in range(linefit, -1, -1)])
eqaverages = [[0 for _ in range(linefit + 1)] for _ in PCs]
divide_by = [0 for _ in PCs]

#Adding corrected capacitance and graphs showing the raw and corrected data as well as the relation between measurements and temperature
for i,df_dos in enumerate(df_doses):
	try:
		pars = temp_correct(df_dos)
	except Exception as e:
		print(e)
		print("No data for {0} within the given daterange.".format(dos_IDs[i]))
		exit()
		
	const_pcs = ['PC3', 'PC4', 'PC5', 'PC6']	
	pcs = ['PC3', 'PC4', 'PC5', 'PC6']
	tpcs = ['TC PC3', 'TC PC4', 'TC PC5', 'TC PC6']
	npcs = ['PCN3', 'PCN4', 'PCN5', 'PCN6']
	
	#For broken pc slots (RIP PC4 Jun 2018)
	if dos_IDs[i] == 'VA00002980T':
		pcs = ['PC3', 'PC5', 'PC6']
		tpcs = ['TC PC3', 'TC PC5', 'TC PC6']
		npcs = ['PCN3', 'PCN5', 'PCN6']
	
	
	for k,j in enumerate([PCs.index(pc) for pc in pcs]):
		eqaverages[j] += pars[j]
		divide_by[j] += 1
	
	
	
	#Raw graph	
	df_dos[['mID'] + pcs].plot(x='mID', title='Raw Measurement Values').set_ylabel('Measurements (fF)')
	pcstdev = [np.std(df_dos[pc].tolist()) for pc in pcs]
	legend_str = ['{0} Std: {1}'.format(pc, round(pcstdev[j],1)) for j, pc in enumerate(pcs)]
	plt.legend(legend_str)
	plt.tight_layout()
	plt.savefig(dos_IDs[i] + '-raw.png')
	
	#Normalized Graph
	df_dos[['mID'] + npcs].plot(x='mID', title='Normalized Measurement Values').set_ylabel('Measurements (fF)')
	plt.legend(pcs)
	plt.tight_layout()
	plt.savefig(dos_IDs[i] + '-norm.png')
	
	#Temperature corrected graph
	df_dos[['mID'] + tpcs].plot(x='mID', title='Corrected Measurement Values').set_ylabel('Measurements (fF)')
	tcstdev = [np.std(df_dos[tpc].tolist()) for tpc in tpcs]
	legend_str = ['{0} Std: {1}'.format(tpc, round(tcstdev[j],1)) for j,tpc in enumerate(tpcs)]
	plt.legend(legend_str)
	plt.tight_layout()
	plt.savefig(dos_IDs[i] + '-tc.png')
	
	#Relationship between Temperature and Measurements graph
	ax = df_dos[['PC1'] + pcs].plot(x='PC1', title='Measurement Values vs. Temperature')
	ax.set_xlabel('Temperature (fF) [PC1]')
	ax.set_ylabel('Measurements (fF)')
	plt.legend(pcs)
	plt.tight_layout()
	plt.savefig(dos_IDs[i] + '-temprel.png')
	
	stdevdf_dosID = pd.DataFrame([[dos_IDs[i]] + pcstdev + tcstdev], columns=['Dosimeter ID'] + pcs + tpcs)
	stdevdf = stdevdf.append(stdevdf_dosID, ignore_index=True)
	eqdata = [[dos_IDs[i], PCs[j]]+ pars[j].tolist() for j in [PCs.index(pc) for pc in pcs]]
	eqdf_dosID = pd.DataFrame(eqdata, columns=['Dosimeter ID', 'PC'] + [x for x in range(linefit, -1, -1)])
	eqdf = eqdf.append(eqdf_dosID)


#Nasty code for average of standard deviation	
sdevavgdata = [['Average'] + [stdevdf['PC' + str(i)].mean() for i in [3,4,5,6]] + [stdevdf['TC PC' + str(i)].mean() for i in [3,4,5,6]]]
stdevdf_avg = pd.DataFrame(sdevavgdata, columns=['Dosimeter ID'] + PCs + TPCs)
stdevdf = stdevdf.append(stdevdf_avg)

#Nasty code for temp correction functions
for i in range(len(dos_IDs)):
	for j in range(len(eqaverages[i])):
		eqaverages[i][j] /= divide_by[i]
		
eqavrgdata = [['Average',  PCs[i]] + eqaverages[i].tolist() for i in range(len(PCs))]
eqavrgdf = pd.DataFrame(eqavrgdata, columns=['Dosimeter ID', 'PC'] + [x for x in range(linefit, -1, -1)])
eqdf = eqdf.append(eqavrgdf)

#print(np.std(df_doses[0]['PC3'].tolist()))

print('DDP_' + DDP.version + ': DDP_configDB_' + DDP.version + ' loaded', end = dash)
print(dash[1:] + 'DDP_' + DDP.version + ': Workbook export initialized', end = dash)


#Saving everything to one notebook
fn = 'export/' + DDP.version + '_' + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.xlsx'  
d = os.path.dirname(fn)
if not os.path.exists(d): os.makedirs(d)
print('DDP_' + DDP.version + ': Saving output- \n' + fn, end = dash)
writer = pd.ExcelWriter(fn, engine='xlsxwriter') #Forces xlsxwriter so that images can be injected
for i,df_dos in enumerate(df_doses):
	df_dos.to_excel(writer, sheet_name=dos_IDs[i])
	writer.sheets[dos_IDs[i]].insert_image('P1', dos_IDs[i] + '-raw.png')
	writer.sheets[dos_IDs[i]].insert_image('P24', dos_IDs[i] + '-norm.png')
	writer.sheets[dos_IDs[i]].insert_image('P47', dos_IDs[i] + '-tc.png')
	writer.sheets[dos_IDs[i]].insert_image('P70', dos_IDs[i] + '-temprel.png')
	
stdevdf.to_excel(writer, sheet_name='Standard Deviations')
eqdf.to_excel(writer, sheet_name='Temperature Correction Values')
writer.save()
print('DDP_' + DDP.version + ': Output saved successfully', end = dash)
print('DDP_' + DDP.version + ': Workbook export completed', end = dash)