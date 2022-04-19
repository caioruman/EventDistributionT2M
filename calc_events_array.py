# coding: utf-8

import xarray as xr
import numpy as np
from glob import glob
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
import os
import argparse
#import os

parser=argparse.ArgumentParser(description='PGW or CTRL', formatter_class=argparse.RawTextHelpFormatter)
#parser.add_argument("-op", "--opt-arg", type=str, dest='opcional', help="Algum argumento opcional no programa", default=False)
parser.add_argument("yeari", type=int, help="Initial Year", default=0)
parser.add_argument("yearf", type=int, help="Final Year", default=0)
parser.add_argument("sim", type=str, help="Simulation Type", default=0)
args=parser.parse_args()

def main(args):

  sim = args.sim

  datai = args.yeari
  dataf = args.yearf
    
  #sim = "CTRL"
  st = f"/chinook/marinier/CONUS_2D/{sim}"

  #datai = 2000
  #dataf = 2013

  store = '/chinook/cruman/Data/Near0Events' 

  ns = 1e-9  

  # annual data
  for y in range(datai, dataf+1):
    print(f"Year: {y}")
    
    for m in range(1, 13):
      print(f"Month: {m}")

      # Open Dataset
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

#      if (m >= 5 and m <= 9):
#        continue

      #if (m < 5 or m > 9):
      #  continue

      if os.path.exists(f"{store}/t2m_{sim}_{y}_{m:02d}.p"):
        print("jump")
        continue      
      
      #/chinook/marinier/CONUS_2D/wrf2d_d01_CTRL_PREC_ACC_NC_200010-200012.nc
      sn = xr.open_dataset(f'{st}/{y}/wrf2d_d01_{sim}_T2_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')      
      pr = xr.open_dataset(f'{st}/{y}/wrf2d_d01_{sim}_PREC_ACC_NC_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')   
      # Slicing the domain to make the computations faster
      #i1=721; j1=1167; i2=874; j2=1333
            
      sn = sn.T2
      pr = pr.PREC_ACC_NC

      xlat = sn.XLAT
      xlon = sn.XLONG
      sn = sn#[:,i1:i2,j1:j2]               

      xlat = xlat#[i1:i2,j1:j2]  
      xlon = xlon#[i1:i2,j1:j2]  

      print(f"Month: {m}")

      datai = datetime.strptime(f'{y}-{m:02d}-01 00:00', '%Y-%m-%d %H:%M')
      dataf = datetime.strptime(f'{y}-{m:02d}-01 00:00', '%Y-%m-%d %H:%M')
      dataf += relativedelta(months=1)
    
      #print(wsn)
      
      sn = sn.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))                 
      pr = pr.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M'))) 
      
      # Boolean array with the places where the temperature is between -2 and 2
      count_bool_le = np.less_equal(sn.values, 271.15)
      count_bool_ge = np.greater_equal(sn.values, 275.15)      
      between = count_bool_ge + count_bool_le
      aux = np.invert(between)
      # Counting all the 1 values in the time dimension
      count = np.count_nonzero(aux.astype(int), axis=0)      
           
      pickle.dump( count, open( f"{store}/t2m_{sim}_{y}_{m:02d}.p", "wb" ) )                  

      # Same thing as above but for precipitation
      sn_pr1 = sn.where(pr > 0.1, 999)
      count_bool_le = np.less_equal(sn_pr1.values, 271.15)
      count_bool_ge = np.greater_equal(sn_pr1.values, 275.15)      
      between = count_bool_ge + count_bool_le
      aux = np.invert(between)
      # Counting all the 1 values in the time dimension
      count = np.count_nonzero(aux.astype(int), axis=0)      
           
      pickle.dump( count, open( f"{store}/t2m_pr01_{sim}_{y}_{m:02d}.p", "wb" ) )

if __name__ == '__main__':
  main(args)
