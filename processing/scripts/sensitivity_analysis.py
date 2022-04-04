import pandas as pd
import xarray as xr
import datetime as dt
import numpy as np
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt

#################################
# define colname to be assessed #
#################################
col = 'JAS_Temp'

# read antarctica's aws file
df = pd.read_csv('../../../antarctica_data/output/antarctica_aws.csv', sep=',', index_col=0, na_values=-9999)

# select data section in file
df_data = df.loc['2021-12-03 00:00:00':].astype(float)
df_data.index.name='time'
ds = xr.Dataset.from_dataframe(df_data)
ds['time'] = pd.to_datetime(ds['time'])

# get times of eclipse from dataframe
l = len('08:55:56') # some random time
ini = dt.datetime.fromisoformat('2021-12-04 ' + df.loc['Start of partial eclipse', col][:l])
mae = dt.datetime.fromisoformat('2021-12-04 ' + df.loc['Maximum eclipse', col][:l])
end = dt.datetime.fromisoformat('2021-12-04 ' + df.loc['End of partial eclipse', col][:l])

x = np.arange(0, 240, 10)
y = np.nan*x

for i, min in enumerate(x):

    print(i)
    # artificial extension of end time eclipse  
    ext = end + dt.timedelta(0,60*int(min))

    # get time series
    temp = ds[col]

    # check for consistency
    # if in a window of 30 min before init there is only nan data, raise error
    bool = ((temp.time >= np.datetime64(ini - dt.timedelta(0,60*30))) & (temp.time < np.datetime64(ini)))
    ini_window = temp.where(bool)
    ini_error = ini_window.isnull().all().values

    # if in a window of 30 min after ext there is only nan data, raise error
    bool = ((temp.time <= np.datetime64(ext + dt.timedelta(0,60*30))) & (temp.time > np.datetime64(ext)))
    ext_window = temp.where(bool)
    ext_error = ext_window.isnull().all().values

    # if in a window between ini and ext there is only nan data, raise error
    bool = ((temp.time <= np.datetime64(ext)) & (temp.time > np.datetime64(ini)))
    int_window = temp.where(bool)
    int_error = int_window.isnull().all().values

    # if in a window between ini and ext there is only nan data, raise error
    ecl_error = temp.sel(time='2021-12-04 ' + df.loc['Maximum eclipse', col][:l], method='nearest').isnull().values

    if ini_error or ext_error or int_error or ecl_error:
        continue

    # starting interpolation

    # set nan data during eclipse
    temp_mod = temp.where((temp.time < np.datetime64(ini)) | (temp.time > np.datetime64(ext)))

    # define x and y data
    y_data = temp_mod.values
    x_data = np.arange(temp_mod.time.values.size)

    # remove nans from x and y data where y is nan
    x_data_nonan = x_data[~np.isnan(y_data)]
    y_data_nonan = y_data[~np.isnan(y_data)]

    # compute x data where interpolation will happen
    bool_time_eclipse_ext = (temp.time >=  np.datetime64(ini)) & (temp.time <= np.datetime64(ext))
    x_data_interp = x_data[bool_time_eclipse_ext]
    time_interp = temp.time.where(bool_time_eclipse_ext, drop=True)

    # perform cubic spline smoothing
    f_smooth_spline = interpolate.splrep(x_data_nonan, y_data_nonan, s=15, k=3)
    y_smooth_spline = interpolate.splev(x_data_interp, f_smooth_spline, der=0)
    
    origin = xr.DataArray(temp.values, coords=[temp.time], dims=['time'])
    smooth = xr.DataArray(y_smooth_spline, coords=[time_interp], dims=['time'])

    # compute observed DT using cubic spline smooth
    dsmooth = (smooth-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()

    # round and format DT
    round_float = lambda z: round(float(z.values), 2)
    y[i] = round_float(dsmooth)

# plot the data
fig = plt.figure(figsize=(12,6))

# plot the curve
plt.plot(x, y,  lw=0.8, c='b')
plt.scatter(x, y,  c='b')

# add labels
plt.xlabel('Extension (min)')
plt.ylabel('Temperature drop (deg C)')
plt.grid(ls='--', lw='0.2', c='grey')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().yaxis.set_ticks_position('left')
plt.gca().xaxis.set_ticks_position('bottom')
plt.show()