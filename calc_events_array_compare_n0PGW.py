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
#parser.add_argument("sim", type=str, help="Simulation Type", default=0)
args=parser.parse_args()

def main(args):

  #sim = args.sim

  datai = args.yeari
  dataf = args.yearf
    
  #sim = "CTRL"
  st_CTRL = f"/chinook/marinier/CONUS_2D/CTRL"
  st_PGW = f"/chinook/marinier/CONUS_2D/PGW"

  #datai = 2000
  #dataf = 2013

  store = '/chinook/cruman/Data/Near0EventsCases' 

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

      if os.path.exists(f"{store}/t2m_near0PGW_{y}_{m:02d}.p"):
        print("jump")
        continue      
      
      #/chinook/marinier/CONUS_2D/wrf2d_d01_CTRL_PREC_ACC_NC_200010-200012.nc
      t2 = xr.open_dataset(f'{st_CTRL}/{y}/wrf2d_d01_CTRL_T2_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')      
      #pr = xr.open_dataset(f'{st_CTRL}/{y}/wrf2d_d01_CTRL_PREC_ACC_NC_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')   
      
      t2_pgw = xr.open_dataset(f'{st_PGW}/{y}/wrf2d_d01_PGW_T2_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')      
      #pr_pgw = xr.open_dataset(f'{st_PGW}/{y}/wrf2d_d01_PGW_PREC_ACC_NC_{y}{mi:02d}-{y}{mf:02d}.nc', engine='netcdf4')   
      # Slicing the domain to make the computations faster
      #i1=721; j1=1167; i2=874; j2=1333
            
      t2 = t2.T2
      #pr = pr.PREC_ACC_NC
        
      t2_pgw = t2_pgw.T2
      #pr_pgw = pr_pgw.PREC_ACC_NC

      xlat = t2.XLAT
      xlon = t2.XLONG
      #sn = sn#[:,i1:i2,j1:j2]               

      #xlat = xlat#[i1:i2,j1:j2]  
      #xlon = xlon#[i1:i2,j1:j2]  

      print(f"Month: {m}")

      datai = datetime.strptime(f'{y}-{m:02d}-01 00:00', '%Y-%m-%d %H:%M')
      dataf = datetime.strptime(f'{y}-{m:02d}-01 00:00', '%Y-%m-%d %H:%M')
      dataf = dataf + relativedelta(months=1) - relativedelta(hours=1)
      
      print(datai, dataf) 
      #print(wsn)
      
      t2 = t2.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))                 
      #pr = pr.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M'))) 
      
      t2_pgw = t2_pgw.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))
      #pr_pgw = pr_pgw.sel(Time=slice(datai.strftime('%Y-%m-%d %H:%M'), dataf.strftime('%Y-%m-%d %H:%M')))

      if y==2005 and m==2:
          t2 = t2.sel(Time=t2_pgw.Time)
       #   pr = pr.sel(Time=pr_pgw.Time)      
        
      # CTRL -8C bin; Boolean array with the places where the temperature is between -12 and -6 in CTRL
      count_bool_le = np.less(t2.values, 261.15)
      count_bool_ge = np.greater_equal(t2.values, 267.15)
      between = count_bool_ge + count_bool_le
      ctrl_minus8 = np.invert(between)
        
      # CTRL -4C bin; Boolean array with the places where the temperature is between -6 and -2 in CTRL
      count_bool_le = np.less(t2.values, 267.15)
      count_bool_ge = np.greater_equal(t2.values, 271.15)
      between = count_bool_ge + count_bool_le
      ctrl_minus4 = np.invert(between)               
    
      # CTRL  0C bin; Boolean array with the places where the temperature is between -2 and +2 in CTRL
      count_bool_le = np.less(t2.values, 271.15)
      count_bool_ge = np.greater_equal(t2.values, 275.15)
      between = count_bool_ge + count_bool_le
      ctrl_near0 = np.invert(between)            
    
      # PGW  0C bin; Boolean array with the places where the temperature is between -2 and 2 in PGW
      count_bool_le = np.less(t2_pgw.values, 271.15)
      count_bool_ge = np.greater_equal(t2_pgw.values, 275.15)      
      between = count_bool_ge + count_bool_le
      pgw_near0 = np.invert(between)           
    
      count = np.count_nonzero(pgw_near0.astype(int), axis=0)           
      pickle.dump( count, open( f"{store}/t2m_near0PGW_{y}_{m:02d}.p", "wb" ) )
             
      count = np.count_nonzero(ctrl_near0.astype(int), axis=0)           
      pickle.dump( count, open( f"{store}/t2m_near0CTRL_{y}_{m:02d}.p", "wb" ) )                  
              
      # Counting all the 1 values in the time dimension and saving the variables
    
      # Cases comparing with near 0C in PGW
      near0PGW_near0CTRL = np.zeros(ctrl_near0.shape)
      near0PGW_near0CTRL[(pgw_near0 == True) & (ctrl_near0 == True)] = 1
      count = np.count_nonzero(near0PGW_near0CTRL.astype(int), axis=0)      
      pickle.dump( count, open( f"{store}/t2m_n0PGW_n0CTRL_{y}_{m:02d}.p", "wb" ) )
        
      near0PGW_m4CTRL = np.zeros(ctrl_near0.shape)
      near0PGW_m4CTRL[(pgw_near0 == True) & (ctrl_minus4 == True)] = 1
      count = np.count_nonzero(near0PGW_m4CTRL.astype(int), axis=0)                 
      pickle.dump( count, open( f"{store}/t2m_n0PGW_m4CTRL_{y}_{m:02d}.p", "wb" ) )
        
      near0PGW_m8CTRL = np.zeros(ctrl_near0.shape)
      near0PGW_m8CTRL[(pgw_near0 == True) & (ctrl_minus8 == True)] = 1
      count = np.count_nonzero(near0PGW_m8CTRL.astype(int), axis=0)                 
      pickle.dump( count, open( f"{store}/t2m_n0PGW_m8CTRL_{y}_{m:02d}.p", "wb" ) )                                  

      
      # Same thing as above but for precipitation
      '''  
      t2_pr = t2.where(pr > 0.2, 999)
      count_bool_le = np.less_equal(t2_pr.values, 271.15)
      count_bool_ge = np.greater_equal(t2_pr.values, 275.15)      
      between = count_bool_ge + count_bool_le
      aux = np.invert(between)
      
      t2_pr = t2_pgw.where(pr_pgw > 0.2, 999)
      count_bool_le = np.less_equal(t2_pr.values, 271.15)
      count_bool_ge = np.greater_equal(t2_pr.values, 275.15)      
      between = count_bool_ge + count_bool_le
      aux_pr = np.invert(between)
    
      near0_both_pr = np.zeros(aux.shape)
      near0_both_pr[(aux == True) & (aux_pr == True)] = 1
      # Counting all the 1 values in the time dimension
      count = np.count_nonzero(near0_both_pr.astype(int), axis=0)      
           
      pickle.dump( count, open( f"{store}/t2m_compare_pr_{y}_{m:02d}.p", "wb" ) )
      '''

if __name__ == '__main__':
  main(args)
