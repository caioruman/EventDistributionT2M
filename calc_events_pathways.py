# coding: utf-8

import xarray as xr
import numpy as np
#import pandas as pd
from glob import glob
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
#import os

sim = "CTRL"
st = f"/chinook/marinier/CONUS_2D/{sim}"

datai = 2001
dataf = 2002

store = '/chinook/cruman/Data/Near0Events'
ns = 1e-9

# Need to change this size later, as the grid is much larger now  
xi=1015 #153
yi = 1359 #166
#xi = 153
#yi = 166
#1015, 1359
aux = np.zeros((xi, yi))
aux13 = np.zeros((xi, yi))
aux24 = np.zeros((xi, yi))
aux1 = np.zeros((xi, yi))
aux2 = np.zeros((xi, yi))
aux3 = np.zeros((xi, yi))
aux4 = np.zeros((xi, yi))

aux_true = np.zeros((xi, yi))
aux_true += 1
aux_false = np.zeros((xi, yi))

aux1_pr = np.zeros((xi, yi))
aux2_pr = np.zeros((xi, yi))
aux3_pr = np.zeros((xi, yi))
aux4_pr = np.zeros((xi, yi))

ini = True
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
        
    t2 = xr.open_dataset(f'{st}/{y}/wrf2d_d01_CTRL_T2_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')
    pr = xr.open_dataset(f'{st}/{y}/wrf2d_d01_CTRL_PREC_ACC_NC_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')
    
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

    #print(wsn)

    t2 = t2.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))
    pr = pr.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))
    
    # first timestep: Set the aux array
    aux = np.logical_and(t2[0]<2, t2[0]>-2)
    
    if not ini:
      # Attach the last value to the first value of the next month.
      #ini = False
      print('ini == false')
      t2 = xr.concat([lastT2, t2], dim='Time')
      pr = xr.concat([lastPR, pr], dim='Time')
      
      lastT2 = t2[-1,:,:]
      lastPR = pr[-1,:,:]
      #sys.exit()
    else:
      lastT2 = t2[-1,:,:]
      lastPR = pr[-1,:,:]
      ini = False
      print('ini == true')

    # second timestep onward: follow the algorithm
    for i in range(1,t2.shape[0]):
      # if the aux == False, event not in place. set the entryways
      # set aux13 and aux24
      new_aux = np.logical_and(t2[i]>-2, t2[i]<2)

      aux13 = np.where((aux==False) & (t2[i-1] > 2), aux_true, aux13)
      aux24 = np.where((aux==False) & (t2[i-1] < -2), aux_true, aux24)
      # I need to keep the previous values of aux13 and aux24 here. if aux=true

      # if the aux == True, event in place. 
      # If the current temperature is between -2 and 2, do nothing. aux continues = True
      # if not, event finished. Calculate the entryways. set aux = False
      aux3 += np.where(((aux13==True) & (t2[i] > 2)) & (aux == True), aux_true, aux_false)            
      aux2 += np.where(((aux24==True) & (t2[i] > 2)) & (aux == True), aux_true, aux_false)

      aux1 += np.where(((aux13==True) & (t2[i] < -2)) & (aux == True), aux_true, aux_false)
      aux4 += np.where(((aux24==True) & (t2[i] < -2)) & (aux == True), aux_true, aux_false)

      # I need to 'reset' the aux13 and aux24
      aux13 = np.where((aux13==True) & (t2[i] > 2), aux_false, aux13)            
      aux13 = np.where((aux13==True) & (t2[i] < -2), aux_false, aux13)
      aux24 = np.where((aux24==True) & (t2[i] > 2), aux_false, aux24)
      aux24 = np.where((aux24==True) & (t2[i] < -2), aux_false, aux24)

      aux = new_aux
    
    # Save stuff, reset aux1234.
    pickle.dump( aux1, open( f"{store}/pathway1_{y}_{m:02d}.p", "wb" ) )
    pickle.dump( aux2, open( f"{store}/pathway2_{y}_{m:02d}.p", "wb" ) )
    pickle.dump( aux3, open( f"{store}/pathway3_{y}_{m:02d}.p", "wb" ) )
    pickle.dump( aux4, open( f"{store}/pathway4_{y}_{m:02d}.p", "wb" ) )

    aux1 = np.zeros((xi, yi))
    aux2 = np.zeros((xi, yi))
    aux3 = np.zeros((xi, yi))
    aux4 = np.zeros((xi, yi))
    #sys.exit()
      