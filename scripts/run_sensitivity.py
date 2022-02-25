#!/usr/bin/python 
# A sample of the sensitivity run script
# Author: Elchin Jafarov
# date: 12.02.2021

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import Sensitivity
import param_util as pu
import time
start=time.time()
driver = Sensitivity.SensitivityDriver()
# change workdir, site, and setup herecru-ts40_ar5_rcp85_ncar-ccsm4_EML_study_area_10x10a
#driver.work_dir='/data/workflows/sensitivity_analysis_EML'
driver.site='/data/input-catalog/cru-ts40_ar5_rcp85_ncar-ccsm4_EML_study_area_10x10'
driver.opt_run_setup = '-p 100 -e 1000 -s 250 -t 115 -n 85'

# setup parameters: 
# Nsamples: number of sample points in the parameter interval
# cmtnum: community type number (site specific)
# params: list of parameter names
# pftnums: list, pft numbers marked by 0 and non pfts by None
# percent_diffs: the difference from the initial value (i.e. initial_value +- initial_value*percent)
# sampling_method: currently only two: lhs and uniform
driver.design_experiment(Nsamples=1, cmtnum=5, params=['cmax','glmax','toptmax','initial_lai','nmax','albvisnir'], 
                         pftnums=[0,0,0,0,0,0], percent_diffs=[.25,.25,.25,.25,.25,.25],
                         sampling_method='lhc')
print(driver.info())

#setup outputs
#print('Setting up the outputs...')
driver.outputs.append({'name': 'RH', 'type': 'xxx'})
driver.outputs.append({'name': 'ALD', 'type': 'xxx'})
driver.outputs.append({'name': 'VEGC', 'type': 'flux'})
#driver.outputs.append({'name': 'SNOWTHICK', 'type': 'xxx'})
#driver.outputs.append({'name': 'RH', 'type': 'xxx'})
#driver.outputs.append({'name': 'VWCLAYER', 'type': 'layer'})
#driver.outputs.append({'name': 'WATERTAB', 'type': 'xxx'})
#driver.outputs.append({'name': 'TLAYER', 'type': 'layer'})
#print(driver.outputs)
#save parameters and sampling matrix in the workflows folder
driver.save_experiment('/data/workflows/')
#process the data (creates the sensitivity.csv files)
#driver.extract_data_for_sensitivity_analysis()
#print('')
try:
    driver.setup_multi()
except ValueError:
    print("Oops!  setup_multi failed.  Check the setup...")

try:
    driver.run_all_samples()
except ValueError:
    print("Oops!  run_all_samples failed.  Check the sample folders...")
#try:
#    driver.sample_matrix()
#except ValueError:
   # print("Oops! extract_data failed..")
#process the data (creates the sensitivity.csv files)
#driver.sample_matrix()
#print('')
print('RUN IS SUCCESSFUL!!!')
end=time.time()
print(end-start)
