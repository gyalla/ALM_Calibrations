"""
The purpose of this script is to interpolate AeroDyn OpenFAST .dat files
to arbitrary number of blade points.

Author: Gopal R. Yalla

"""
import numpy as np
import pandas as pd
import re
from scipy.interpolate import interp1d


################################################################################
#Inputs 
################################################################################
#Location of existing AeroDyn .dat file
turbineDirIn = './'
#inFile = turbineDirIn + 'IEA-15-240-RWT_AeroDyn15_blade.dat'
inFile = turbineDirIn + 'NRELOffshrBsline5MW_AeroDyn_blade.dat'

#New number of Aerodyn blade points to use
num_interp_points = 300 

#Name of new AeroDyn .dat file
turbineDirOut = './'
#outFile = turbineDirOut + 'IEA-15-240-RWT_AeroDyn15_blade_'+str(num_interp_points)+'.dat'
outFile = turbineDirOut + 'NRELOffshrBsline5MW_AeroDyn_blade_'+str(num_interp_points)+'.dat'

################################################################################
#Interpolation AeroDyn Information
################################################################################
df = pd.read_csv(inFile,delim_whitespace=True,skiprows=[0,1,2,3,5])

with open(inFile,'r') as f:
    lines = f.readlines()

orig_points = np.asarray(df['BlSpn'])
minx = orig_points[0]
maxx = orig_points[-1]

interp_points = np.linspace(minx,maxx,num_interp_points)

lines[3] = re.sub(r'^\d+', str(num_interp_points), lines[3])

interpolator_kind = 'linear' 
interp_data = np.zeros((num_interp_points,len(df.keys())))
for key_counter, key in enumerate(df.keys()):
    #if not key == 'BlAFID':
    print("Interpolating: ",key)
    interpolator  = interp1d(orig_points,np.asarray(df[key]),kind=interpolator_kind)
    interp_data[:,key_counter]  = interpolator(interp_points)

interp_df = pd.DataFrame(interp_data,columns=df.keys())

#for i,point in enumerate(interp_df['BlSpn']):
#    idx = (np.abs(df['BlSpn']-point)).argmin() #nearest blade section interpolation 
#    print(idx)
#    interp_df['BlAFID'][i] = idx+1

scientific_format = '{:0.15e}'
integer_format = '{:d}'

column_formats = {}
for column in interp_df.columns:
    if column == 'BlAFID':
        column_formats[column] = integer_format
    else:
        column_formats[column] = scientific_format

with open(outFile,'w') as f:
    lines[3] = re.sub(r'^\s*\d+', str(num_interp_points), lines[3])
    for line in lines[0:6]:
        f.write(line)

    for _,row in interp_df.iterrows():
        for col,val in row.items():
            if col == "BlAFID":
                val = int(val)
            f.write(column_formats[col].format(val))
            f.write(" ")
        f.write('\n')

