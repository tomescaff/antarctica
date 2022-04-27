import pandas as pd
import xarray as xr
import datetime as dt
import numpy as np
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt

# read table base from csv
df = pd.read_csv('../../../antarctica_data/output/antarctica_aws.csv', sep=',', index_col=0, na_values=-9999)

# select header section
df_header = df.loc[:'Best timedelta (hrs)']

# select data section
df_data = df.loc['2021-12-03 00:00:00':].astype(float)
df_data.index.name='time'

# prepare index for output table
mins = np.arange(0, 210, 10)
index_header = df_header.index.tolist()
index_data = df_data.index.tolist()
index_new = ['ini error', 
             'end error', 
             'int error', 
             'ecl error']
index_new = ['DTbest 8UTC']
# index_new += ["DTmax {} min spline smooth".format(ext_min) for ext_min in mins]

# create xarray dataset
ds = xr.Dataset.from_dataframe(df_data)
ds['time'] = pd.to_datetime(ds['time'])

columns = list(ds.keys())

for col in columns:

    # smoothing parameter
    best_s = float(df_header.loc['Best S', col])

    # extra time for computing interpolation
    best_dt = float(df_header.loc['Best timedelta (hrs)', col])

    if df_header.loc['QA', col] == 'bad':
        continue 

    
    # get times of eclipse from dataframe
    l = len('08:55:56') # some random time
    ini = dt.datetime.fromisoformat('2021-12-04 ' + df.loc['Start of partial eclipse', col][:l])
    mae = dt.datetime.fromisoformat('2021-12-04 ' + df.loc['Maximum eclipse', col][:l])
    end = dt.datetime.fromisoformat('2021-12-04 ' + df.loc['End of partial eclipse', col][:l])

    # get time series
    temp = ds[col]

    # check for consistency
    # if in a window of 30 min before init there is only nan data, raise error
    bool = ((temp.time >= np.datetime64(ini - dt.timedelta(0,60*30))) & (temp.time < np.datetime64(ini)))
    ini_window = temp.where(bool)
    ini_error = ini_window.isnull().all().values
    df.loc['ini error', col] = ini_error

    # if in a window of 30 min after ext there is only nan data, raise error
    bool = ((temp.time <= np.datetime64(end + dt.timedelta(0,60*30))) & (temp.time > np.datetime64(end)))
    end_window = temp.where(bool)
    end_error = end_window.isnull().all().values
    df.loc['end error', col] = end_error

    # if in a window between ini and ext there is only nan data, raise error
    bool = ((temp.time <= np.datetime64(end)) & (temp.time > np.datetime64(ini)))
    int_window = temp.where(bool)
    int_error = int_window.isnull().all().values
    df.loc['int error', col] = int_error

    # if in a window between ini and ext there is only nan data, raise error
    ecl_error = temp.sel(time='2021-12-04 ' + df.loc['Maximum eclipse', col][:l], method='nearest').isnull().values
    df.loc['ecl error', col] = ecl_error

    ############################
    # starting interpolation
    ############################

    ext_min = best_dt*60
    
    # artificial extension of end time eclipse  
    ext = end + dt.timedelta(0,60*int(ext_min)) 

    # set nan data during eclipse
    temp_mod = temp.where((temp.time < np.datetime64(ini)) | (temp.time > np.datetime64(ext)))

    # define x and y data
    y_data = temp_mod.values
    x_data = np.arange(temp_mod.time.values.size)

    # remove nans from x and y data where y is nan
    x_data_nonan = x_data[~np.isnan(y_data)]
    y_data_nonan = y_data[~np.isnan(y_data)]

    # compute x data where interpolation will happen
    bool_time_eclipse_ext = (temp.time == temp.sel(time='2021-12-04 08:00:00').time.values)
    x_data_interp = x_data[bool_time_eclipse_ext]
    time_interp = temp.time.where(bool_time_eclipse_ext, drop=True)


    # perform cubic spline smoothing

    try:
        f_smooth_spline = interpolate.splrep(x_data_nonan, y_data_nonan, s=best_s, k=3)
        y_smooth_spline = interpolate.splev(x_data_interp, f_smooth_spline, der=0)
    except Exception as e:
        df.loc["DTmax {} spline smooth".format(ext_min), col] = np.nan
        continue
    
    # calculate the max DT during eclipse (not extended eclipse)
    origin = xr.DataArray(temp.values, coords=[temp.time], dims=['time'])
    smooth = xr.DataArray(y_smooth_spline, coords=[time_interp], dims=['time'])

    dsmooth = (smooth-origin).sel(time='2021-12-04 08:00:00')

    round_float = lambda x: round(float(x.values), 2)

    df.loc["DTmax {} min spline smooth".format(ext_min), col] = round_float(dsmooth)
    
    df.loc["DTbest 8UTC", col] = round_float(dsmooth)

df = df.reindex(index_header + index_new + index_data)
df = df.fillna(value = -9999)
df = df.replace(-9999.00, '-9999')
df.to_csv('../../../antarctica_data/output/antarctica_aws_dtobs__spline_smooth_bestparms_8UTC.csv', sep=',')
