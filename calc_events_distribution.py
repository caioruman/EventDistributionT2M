# coding: utf-8

import xarray as xr
import numpy as np
#import pandas as pd
from glob import glob
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
import argparse
#import os

parser=argparse.ArgumentParser(description='PGW or CTRL', formatter_class=argparse.RawTextHelpFormatter)
#parser.add_argument("-op", "--opt-arg", type=str, dest='opcional', help="Algum argumento opcional no programa", default=False)
parser.add_argument("yeari", type=int, help="Initial Year", default=0)
parser.add_argument("yearf", type=int, help="Final Year", default=0)
parser.add_argument("sim", type=str, help="Simulation Type", default=0)
args=parser.parse_args()

#sim = "CTRL"
#sim = "PGW"
sim = args.sim
st = f"/chinook/marinier/CONUS_2D/{sim}"

datai = args.yeari
dataf = args.yearf

store = '/chinook/cruman/Data/Near0Events/Distribution'
ns = 1e-9

# Need to change this size later, as the grid is much larger now  
xi = 1015 #153
yi = 1359 #166
#xi = 153
#yi = 166
l = np.arange(-50,48,4)
dist = np.zeros((xi, yi, len(l)))

aux = np.full((xi, yi), True)

aux_true = np.full((xi, yi), True)
aux_false = np.full((xi, yi), False)

aux_pr = np.full((xi, yi), False)

for y in range(datai, dataf+1):
  print(f"Year: {y}")

  for m in range(1, 13):

# Open Dataset
    print(f"Month: {m}")
    if 1 <= m <= 3:
      mi = 1
      mf = 3
    elif 4 <= m <= 6:
      mi = 4
      mf = 6
    elif 7 <= m <= 9:
      mi = 7
      mf = 9
    else:
      mi = 10
      mf = 12

    if (y == 2000) and m < 10:
      continue

    if (y == 2013) and m > 9:
      continue
        
    t2 = xr.open_dataset(f'{st}/{y}/wrf2d_d01_{sim}_T2_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')
    pr = xr.open_dataset(f'{st}/{y}/wrf2d_d01_{sim}_PREC_ACC_NC_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')
    
    # Slicing the domain to make the computations faster
    #i1=721; j1=1167; i2=874; j2=1333
    t2 = t2.T2
    
    pr = pr.PREC_ACC_NC 

    xlat = t2.XLAT
    xlon = t2.XLONG
    #t2 = t2[:,i1:i2,j1:j2] 
    #pr = pr[:,i1:i2,j1:j2]
    
    t2 = t2 - 273.15
    
    datai = datetime.strptime(f'{y}-{m:02d}-01 00:00', '%Y-%m-%d %H:%M')
    dataf = datetime.strptime(f'{y}-{m:02d}-01 00:00', '%Y-%m-%d %H:%M')
    dataf += relativedelta(months=1)
    dataf -= relativedelta(hours=1)    

    t2 = t2.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))
    pr = pr.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))          

    # Loop throught the l array and compute the distribution for each grid point
    #for t in range(1,t2.shape[0]):
    for i in range(len(l)):
      # if first item
      if i == 0:        
        aux = np.where(t2<l[i], aux_true, aux_false)
      # last item
      elif i == len(l)-1:
        aux = np.where(t2>=l[i], aux_true, aux_false)
        # do something else
      # all the other numbers
      else:
        aux = np.logical_and(t2>=l[i-1], t2<l[i])

      # sum the time axis
      aux = np.sum(aux, axis=0)
      # add to the distribution
      dist[:,:,i] += aux
    
    # Save stuff, reset aux1234.
    pickle.dump( dist, open( f"{store}/dist_{sim}_{y}_{m:02d}.p", "wb" ) )    
    dist = np.zeros((xi, yi, len(l)))
    #sys.exit()
      
