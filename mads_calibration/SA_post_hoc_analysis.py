#!/usr/bin/env python

# import os
# import yaml

# import drivers.Sensitivity

# # THis is how you can setup and work with a driver for runs that are already
# # done...i.e. there should be output data in the ssrfs...
# #
# # Note that if you try to use this with a config file that has more stuff
# # enabled than the run was originally done with it should fail...

# WORK_PATH = '/data/workflows/CMT06_IMNAVIAT_GPPAINcmax_TBC'
# WORK_PATH = '/Users/tobeycarman/Documents/SEL/dvmdostem-workflows/CMT06_IMNAVIAT_GPPAINcmax_TBC'

# driver = drivers.Sensitivity.SensitivityDriver()

# driver.set_work_dir(WORK_PATH)

# driver.load_experiment(os.path.join(WORK_PATH, 'SA', 'param_props.csv'),
#                        os.path.join(WORK_PATH, 'SA', 'sample_matrix.csv'),
#                        os.path.join(WORK_PATH, 'SA', 'info.txt'), )

# # Should these be part of the save/load functionality?
# driver.set_seed_path('/work/parameters/')
# driver.load_target_data('/work/calibration/')

# with open('CMT06_IMNAVIAT_GPPAINcmax_TBC.yaml', 'r') as config_data:
#     config = yaml.safe_load(config_data)

# driver.setup_outputs(config['target_names'])

import os
import numpy as np
import pandas as pd
import sklearn.metrics as sklm
import scipy.stats
import matplotlib.pyplot as plt
# import Line2D to manually create legend handles
from matplotlib.lines import Line2D


# This stuff is diamond box in SA (orange half)
def plot_boxplot(results, targets):
  '''
  Plots a box and whiskers for each column in ``results``. Plots a dot for
  each target value.

  Useful for seeing if the range of model outputs produced by running each row
  in the sample matrix contains the target values.

  .. image:: /images/SA_post_hoc_analysis/results_boxplot.png
     :width: 80%

  Parameters
  ----------
  results : pandas.DataFrame
    One column for each model ouput variable, one row for each run (sample)

  targets : pandas.DataFrame
    One column for each target (truth, or observation) value. One row.
  '''
  plt.close('all')
  fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(6,6))
  results.boxplot(ax=ax, rot=45)
  ax.scatter(range(1,len(targets.columns)+1), targets, color='red', zorder=1000)
  plt.savefig("plots/results_boxplot.png")

def plot_spaghetti(results, targets):
  '''
  Plots one line for each sample (row) in ``results``. Plots targets as dots.
  X axis of plot are for different columns in ``results``. Makes 2 plots, the 
  right one uses a log scale for the y axis.

  Useful for seeing if the range of model outputs produced by running each row
  in the sample matrix contains the target values.

  .. image:: /images/SA_post_hoc_analysis/spaghetti_plot.png

  Parameters
  ----------
  results : pandas.DataFrame
    One row for each run (sample), one column for each model output variable.
  
  targets : pandas.DataFrame
    Single row, one column for each target (truth, or observation) value.
  '''
  plt.close('all')
  fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2,figsize=(24,6))

  for i, sample in results.iterrows():
    ax1.plot(sample, color='gray', alpha=0.1)

  # ax1.plot(results.mean(), color='blue')
  # ax1.fill_between(range(len(results.T)),
  #                 results.mean() - results.std(), 
  #                 results.mean() + results.std(),
  #                 color='gray', alpha=.5, linewidth=0)
  # ax1.fill_between(range(len(results.T)),
  #                 results.min(), 
  #                 results.max(),
  #                 color='gray', alpha=.25, linewidth=0)

  ax2.plot(results.mean(), color='blue')
  for i, sample in results.iterrows():
    ax2.plot(sample, color='gray', alpha=0.1)

  # Targets
  for ax in [ax1, ax2]:
    ax.scatter(range(len(targets.T)), targets, 
               marker='o', color='red', zorder=1000)

  ax2.set_yscale('log')

  plt.savefig("plots/spaghetti_plot.png")

def plot_match(results, targets):
  '''
  Plot targets vs model outputs (results). Dashed diagonal is line of perfect 
  agreement between the model output and the targets. Plot dot or marker for
  each model output. Targets are on the y axis, model outputs on the x axis.

  The result a horizontal collection of markers for each column in results.
  If the collection of markers crosses the dashed 1:1 line, then the model
  is capable of producing target values somewhere in the sample set. If the
  collection of markers for a given column (model output) is all to the left
  of the 1:1 line, then the modeled values are all too low. If the collection of
  markers is all to the right of the 1:1 line then the modeled values are too
  high.

  .. image:: /images/SA_post_hoc_analysis/one2one_match.png
  
  '''
  # "One to one match plot"
  plt.close('all')
  fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,12))

  x = np.linspace(targets.min(axis=1), targets.max(axis=1), 10)
  ax.plot(x,x, 'b--')
  ax.scatter(results, [targets for i in range(len(results))], alpha=.1)

  plt.savefig("plots/one2one_match.png")




# ut.get_param_r2_rmse()

# This stuff is all about revising (tightening parameter ranges) leads into blue box
def calc_metrics(results, targets):
  '''Calculate a bunch of sklearn regression metrics.'''
  # This is gonna need some help...not seeming to pick the right stuff.\
  # not sure if weights should be passed to metrics function, like this:
  #
  #    weights_by_targets = targets.values[0]/targets.sum(axis=1)[0]
  #    r2 = [sklm.r2_score(targets.T, sample, sample_weight=weights_by_targets) for i,sample in results.iterrows()]

  r2 = [sklm.r2_score(targets.T, sample) for i,sample in results.iterrows()] 
  rmse = [sklm.mean_squared_error(targets.T, sample, squared=False) for i,sample in results.iterrows()]
  mape = [sklm.mean_absolute_percentage_error(targets.T, sample) for i,sample in results.iterrows()]

  return r2, rmse, mape

def calc_correlation(model_results, sample_matrix):
  '''
  Generate a correlation matrix between parameters and model outputs.

  Parameters
  ----------
  sample_matrix: pandas.DataFrame
    with one row per sample, one column per parameter
  model_results: pandas.DataFrame
    with one row per sample, one column per output

  Returns
  -------
  corr_mp: pandas.DataFrame
    One column for each parameter, one row for each model output.
  '''
  # correlation between model outputs and parameters
  corr_mp = pd.DataFrame(columns=sample_matrix.columns, index=model_results.columns)

  for model_col in model_results.columns:
    for param_col in sample_matrix.columns:
        corr = model_results[model_col].corr(sample_matrix[param_col])
        corr_mp.loc[model_col, param_col] = corr

  corr_mp = corr_mp.astype(float)

  return corr_mp

def plot_relationships(results, sample_matrix, targets, variables=None, parameters=None, corr_threshold=None, save=None):
  '''
  Look at the model outputs and the parameters, calculate the corrleation
  between the two, and then make one plot for each instance where the
  correlation exceeds the threshold.

  Parameters
  ----------
  results: pandas.DataFrame
    One row per sample, one column per output.
  sample_matrix: pandas.DataFrame
    One row per sample, one column per parameter.
  targets: pandas.DataFrame
    One row with one column per target value.
  variables: list, optional
    Strings referencing variables of interest in results
  parameter: list, optional
    Strings referencing parameers of interest in sample_matrix
  corr_threshold: float, optional
    Lower threshold for correlation to plot
  save: optional
    Saves all subplots (can be a lot) if != None

  Returns
  -------
  None

  .. image:: /images//INGPP_pft0-cmax_pft0-cmax_pft3.png

  '''
  # if variables/parameters are None plot all variables/parameters
  if variables == None:
    variables = list(results.columns.values)
  if parameters == None:
    parameters = list(sample_matrix.columns.values)
    
  # Calculate correlation
  corr = calc_correlation(results, sample_matrix)

  # loop through variables and create set of subplots for each
  for vars in variables:
    # Create a square of subplots from square root of number of parameters per variable
    fig_size = int(np.ceil(np.sqrt(len(parameters))))
    # Create indices for looping through subplot columns
    col_indices = np.linspace(0, fig_size - 1, fig_size).astype(int)
    # Create subplots
    if len(parameters) < 3:
      fig, ax = plt.subplots(1, fig_size)
      # Create indices for looping through subplot rows
      row_indices = [1]
    else:
      fig, ax = plt.subplots(fig_size, fig_size)
      # Create indices for looping through subplot rows
      row_indices = np.linspace(0, fig_size - 1, fig_size).astype(int)
        
    # Counter for results column number during subplot looping
    count = 0

    # Looping through rows and columns in subplot square
    for row in row_indices:  
      for col in col_indices:
        # Catch if only looking at a single row of subplots
        if len(row_indices) <= 1:
          axis = ax[col]
          plt.setp(ax[0], ylabel=vars)
        else:
          axis = ax[row, col]
          plt.setp(ax[:, 0], ylabel=vars)

        if corr_threshold != None:
          if corr.loc[vars, parameters[count]] < corr_threshold:
            # Setting title (corr) 
            axis.set_title(corr.loc[vars, parameters[count]])
            # Setting xlabel (parameter name) 
            axis.set_xlabel(parameters[count])
            #Do not plot as below correlation threshold
            break
          elif corr.loc[vars, parameters[count]] >= corr_threshold:
            # Plotting scatter of parameter, variable relationship
            axis.scatter(sample_matrix[parameters[count]], results[vars])
            # Plotting target value line
            axis.plot(sample_matrix[parameters[count]], targets[vars].values*np.ones(len(sample_matrix[parameters[count]])), 'k--')
            # Setting xlabel (parameter name) 
            axis.set_xlabel(parameters[count])
            # Setting title (corr) 
            axis.set_title(corr.loc[vars, parameters[count]])
            # Go to next output variable
            count+=1
        else:
          # Plotting scatter of parameter, variable relationship
          axis.scatter(sample_matrix[parameters[count]], results[vars])
          # Plotting target value line
          axis.plot(sample_matrix[parameters[count]], targets[vars].values*np.ones(len(sample_matrix[parameters[count]])), 'k--')
          # Setting xlabel (parameter name) 
          axis.set_xlabel(parameters[count])
          # Go to next output variable
          count+=1
          # Break loop if we reach maximum number of columns before number of subplots
          if count > (len(parameters) - 1):
            break
      # Create a single legend with all handles provided outside of subplots
      legend_info = [Line2D([0], [0], color='k', linewidth=3, linestyle='--'),
                     Line2D([0], [0], marker='o', markersize=5, markeredgecolor='C0', markerfacecolor='C0', linestyle='')]
      legend_labels = ["Observations", "Model"]
      plt.legend(legend_info, legend_labels, bbox_to_anchor=(1.05, 1.0), loc="upper left", fontsize=10)
      # Adjust spacing between subplots
      plt.subplots_adjust(left=None, bottom=None, right=1, top=1.2, wspace=None, hspace=None)
      # Save figure if enabled - may create a large number of figures
      if save != None:
        plt.savefig(f"plots/{vars}-{'-'.join(parameters)}.png", bbox_inches="tight")

def plot_corr_heatmap(df_corr):
  '''
  ??? Write something...

  .. image:: /images/SA_post_hoc_analysis/correlation_heatmap.png

  '''
  import seaborn

  plt.figure(figsize=(15,10))
  seaborn.heatmap(df_corr, cmap="YlGnBu", annot=True, fmt=".2f")
  plt.title("Correlation Matrix [Results vs Parameters]", fontsize=16)
  plt.ylabel("Model Results", fontsize=14)
  plt.xlabel("Parameters", fontsize=14)
  plt.savefig("plots/correlation_heatmap.png")

def plot_output_scatter(results, targets, r2lim=None, rmselim=None, mapelim=None):
  '''
  Create subplots for each column in ``results``. Each subplot shows
  scatter plots of the output value on the Y axis and the sample # on the X
  axis. The target value is shown as a dashed line.

  Optionally, ``results`` may be limited by R^2, RMSE, and/or MAPE by providing
  limits using r2lim, rmselim, and mapelim respectively.

  .. note::

    Not sure if this approach of putting everything in one giant figure will
    scale up with number of output variables very well...

  Parameters
  ==========
  results : pandas.DataFrame
    One column for each output variable, one row for each sample run.

  targets : pandas.DataFrame
    One column for each output (target) variable, single row with target value.

  r2lim : float, optional
    Lower R^2 limit for output.

  rmse2lim : float, optional
    Upper RMSE limit for output.

  mape2lim : float, optional
    Upper MAPE limit for output.

  Returns
  =======
  None

  .. image:: /images/SA_post_hoc_analysis/output_target_scatter.png
  '''
  # Calculate r2, rmse, mape metrics and create pandas data series
  r2, rmse, mape = calc_metrics(results, targets)
  df_r2 = pd.Series( r2,  name = '$R^2$'  )
  df_rmse = pd.Series( rmse,  name = 'RMSE'  )
  df_mape = pd.Series( mape,  name = 'MAPE'  )

  # Create a square of subplots based on the square root of number of columns
  fig_size = int(np.ceil(np.sqrt(len(results.columns))))
  # Create indices for looping through subplots
  fig_indices = np.linspace(0, fig_size - 1, fig_size).astype(int)
  # Create subplots
  fig, ax = plt.subplots(fig_size, fig_size)
    
  # Counter for results column number during subplot looping
  count = 0
    
  # Looping through rows and columns in subplot square
  for row in fig_indices:     
    # Break loop if we reach maximum number of columns before number of subplots
    if count > len(results.columns):
      break

    for col in fig_indices:
      # Plot target line across number of samples
      ax[row, col].plot(results.index, np.ones(len(results.index)) * targets[targets.columns[count]].values, 'k--')
      # Scatter plots for results from all samples
      ax[row, col].scatter(results.index,results[results.columns[count]])
      # Title each subplot with output variable, pft, compartment
      ax[row, col].set_ylabel(results.columns[count])
      # If an R^2 limit is given plot all results above that value
      if r2lim != None:
        ax[row, col].scatter(results[df_r2>r2lim].index, results[df_r2>r2lim][results.columns[count]])
      # If an RMSE limit is given plot all results below that value
      if rmselim != None:
        ax[row, col].scatter(results[df_rmse<rmselim].index, results[df_rmse<rmselim][results.columns[count]])
      # If a MAPE limit is given plot all results below that value
      if mapelim != None:
        ax[row, col].scatter(results[df_mape<mapelim].index, results[df_mape<mapelim][results.columns[count]])
      # Go to next output variable
      count+=1
  # Create a single legend with all handles provided outside of subplots
  legend_info = [Line2D([0], [0], color='k', linewidth=3, linestyle='--'),
                 Line2D([0], [0], marker='o', markersize=5, markeredgecolor='C0', markerfacecolor='C0', linestyle=''),
                 Line2D([0], [0], marker='o', markersize=5, markeredgecolor='C1', markerfacecolor='C1', linestyle=''),
                 Line2D([0], [0], marker='o', markersize=5, markeredgecolor='C2', markerfacecolor='C2', linestyle=''),
                 Line2D([0], [0], marker='o', markersize=5, markeredgecolor='C3', markerfacecolor='C3', linestyle='')]
  legend_labels = ['Observations', 'Model', f'R$^2$>{r2lim}',f'RMSE<{rmselim}', f'MAPE<{mapelim}']
  plt.legend(legend_info, legend_labels, bbox_to_anchor=(1.05, 1.0), loc="upper left", fontsize=10)
  # Adjust spacing between subplots
  plt.subplots_adjust(left=None, bottom=None, right=1.2, top=1.2, wspace=None, hspace=None)
  # Add mutual x axis label
  plt.setp(ax[-1, :], xlabel='Sample number')
  # Save figure
  plt.savefig('plots/output_target_scatter.png')

def plot_r2_rmse(results, targets):
  '''
  Plot ???

  .. image:: /images/SA_post_hoc_analysis/r2_mse_mape.png

  '''

  r2, rmse, mape = calc_metrics(results, targets)

  plt.close('all')
  fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12,12))

  axes[0].plot(r2,rmse, 'o', alpha=.5)
  axes[0].set_xlabel('r2')
  axes[0].set_ylabel('rmse')
  #axes[0].set_yscale('log')

  axes[1].plot(r2, mape, 'o', alpha=0.25)
  axes[1].set_xlabel('r2')
  axes[1].set_ylabel('mape')

  plt.legend()

  plt.savefig("plots/r2_rmse_mape.png")

def calc_combined_score(results, targets):
  '''Calculate a combination score using r^2, and normalized mse and mape.'''

  r2, rmse, mape = calc_metrics(results, targets)

  # normalize mse and mape to be between 0 and 1
  norm_rmse = (rmse - np.nanmin(rmse)) / (np.nanmax(rmse) - np.nanmin(rmse))
  norm_mape = (mape - np.nanmin(mape)) / (np.nanmax(mape) - np.nanmin(mape))

  # combined accuracy by substracting average of mse and mape from r2
  combined_score = r2 - np.mean([norm_rmse, norm_mape])

  return combined_score

def generate_ca_config():
  '''Maybe we should auto-generate the yaml config files?'''
  pass  

def prep_mads_initial_guess(params):
  '''
  Generate MADS initial guess string based on parameter ranges. The idea is that
  the intial guess should be the mean of the parameter range. Gives you
  a string like this:

    .. code:: 

      mads_initialguess:
        - 16.252  # cmax_pft0
        - 79.738  # cmax_pft1
        - 44.687  # cmax_pft2

  that is intended to be copied into your ``.yaml`` config file.

  Parameters
  ----------
  params : pandas.DataFrame
    A DataFrame containing parameter values.

  Returns
  -------
  str
    MADS initial guess string.
  '''
  # First get the min and max for each column
  ranges = [(params[x].min(), params[x].max(), x) for x in params]

  s2 = 'mads_initialguess:\n'
  for MIN, MAX, comment in ranges:
    s2 += f"- {scipy.stats.uniform(loc=MIN, scale=MAX-MIN).mean():8.3f}  # {comment}\n"

  return s2

def prep_mads_distributions(params):
  '''
  Gives you something like this:

  .. code::

    mads_paramdist:
      - Uniform(  5.9117,  26.5927)    # cmax_pft0
      - Uniform( 46.0129, 113.4639)    # cmax_pft1
      - Uniform( 11.7916,  77.5827)    # cmax_pft2

  From B. Maglio's notebook.

  Parameters
  ----------
  params : pandas.DataFrame
    One row for each of the selected runs, one column for each parameter.
    Column names are

  Returns
  -------
  dists : string
    A nicely formatted string with the distributions for each parameter that can be
    pasted into the .yaml file for the next step.
  '''

  # First get the min and max for each column
  ranges = [(params[x].min(), params[x].max(), x) for x in params]

  # Then make a nice string out of it...
  s = 'mads_paramdist:\n'
  for MIN, MAX, comment in ranges:
    s += f"- Uniform({MIN:8.3f}, {MAX:8.3f})    # {comment}\n"


  return s

def n_top_runs(results, targets, params, r2lim, N=None):
  '''
  Get the best runs measured using R^2, if N is present sort and return
  N top runs.

  Parameters
  ==========
  results : pandas.DataFrame
    One column for each output variable, one row for each sample run.

  targets : pandas.DataFrame
    One column for each output (target) variable, single row with target value.

  params : pandas.DataFrame
    One row for each of the selected runs, one column for each parameter.

  r2lim : float
    Lower R^2 limit for output.
  
  N : integer, optional
    Number of sorted results to return

  Returns
  -------
  best_params : pandas.DataFrame
    parameters returning variables above R^2 threshold from target value, sorted 
    top N number if None!=None

  best_results : pandas.DataFrame
    results above R^2 threshold from target value, sorted
    top N number if None!=None

  '''
  # Calculate r2, rmse, mape metrics and create pandas data series
  r2, rmse, mape = calc_metrics(results, targets)
  df_r2 = pd.Series( r2,  name = '$R^2$'  )

  if N != None:
      best_indices = np.argsort(df_r2)
      sorted_params = params.iloc[best_indices]
      sorted_results = results.iloc[best_indices]
      best_params = sorted_params[:N]
      best_results = sorted_results[:N]
  else:
      best_params = params[df_r2>r2lim]
      best_results = results[df_r2>r2lim]

  return best_params, best_results

def read_mads_iterationresults(iterationresults_file):
  '''
  Parse a Mads .iterationresults file and return data as 3 python lists.

  Example of the input file: 

  .. code::

    OrderedCollections.OrderedDict("cmax_pft0" => 26.245, "cmax_pft1" => ... )
    OF: 1.985656773338984e8
    lambda: 4.0e9
    OrderedCollections.OrderedDict("cmax_pft0" => 26.245, "cmax_pft1" => ... )
    OF: 1.6545342e4353453e6
    lambda: 1.4e6
  '''

  with open(iterationresults_file) as f:
    data = f.readlines()

  OF = []
  OPT = []
  LAM = []
  for i in data:
    if 'OF:' in i:
      OF.append(i.strip())
    if 'OrderedCollections.OrderedDict' in i:
      OPT.append(i.strip())
    if 'lambda:' in i:
      LAM.append(i.strip())

  def pyobjfromjl(a):
    '''
    This is a dangerous function!

    Use at your own risk and make sure your inputs are good!
    '''
    a = a.replace('=>','=')
    a = a.replace('OrderedCollections.OrderedDict', 'dict')
    a = a.replace('"','')
    return eval(a)

  OPT = [pyobjfromjl(x) for x in OPT]
  OF = [dict(OF=float(x.strip().split(':')[1].strip())) for x in OF]
  LAM = [dict(lam=float(x.strip().split(':')[1].strip())) for x in LAM]

  return OPT, OF, LAM

def load(path):
  '''
  Load up pandas.DataFrames for all the various things that you will want to
  analyze. This includes the parameter properties used for the SA, the
  sample matrix, the target data and the model results.

  Parameters
  ----------
  path: str
    A file path to a directory that is expected to have the following files:
    param_props.csv, sample_matrix.csv, targets.csv, results.csv.

  Returns
  -------
  param_props, sample_matrix, targets, results
  '''

  param_props = pd.read_csv(os.path.join(path, 'param_props.csv'))
  sample_matrix = pd.read_csv(os.path.join(path, 'sample_matrix.csv'))
  targets = pd.read_csv(os.path.join(path, 'targets.csv'), skiprows=1)
  results = pd.read_csv(os.path.join(path, 'results.csv'))

  return param_props, sample_matrix, targets, results

def get_parser():
  pass

def cmdline_parse():
  pass

def cmdline_run():
  pass

def cmdline_entry():
  pass

if __name__ == '__main__':

  # EXAMPLES HERE OF WHAT YOUR IPYTHON SESSION MIGHT LOOK LIKE.....

  # Load data
  param_props = pd.read_csv('SA/param_props.csv')
  sample_matrix = pd.read_csv("SA/sample_matrix.csv")
  targets = pd.read_csv('SA/targets.csv', skiprows=1)
  results = pd.read_csv('SA/results.csv')


  # # Trying to print out the bounds so we can get updated improved bounds after
  # # SA and getting n_top_runs...
  # lower, upper = row.strip().lstrip('[').rstrip(']').split(',')

  # #driver.collect_all_outputs()
  # from IPython import embed; embed()
    
