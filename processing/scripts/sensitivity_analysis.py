import pandas as pd
import xarray as xr
import datetime as dt
import numpy as np
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt

df = pd.read_csv('../../../antarctica_data/output/antarctica_aws.csv', sep=',', index_col=0, na_values=-9999)
df_data = df.loc['2021-12-03 00:00:00':].astype(float)
df_data.index.name='time'
ds = xr.Dataset.from_dataframe(df_data)
ds['time'] = pd.to_datetime(ds['time'])

col = 'JAS_Temp'

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

    # # perform linear interpolation
    # f_lineal = interp1d(x_data_nonan, y_data_nonan)
    # y_lineal = f_lineal(x_data_interp)

    # # perform cubic spline interpolation
    # f_interp_spline = interpolate.splrep(x_data_nonan, y_data_nonan, s=0, k=3)
    # y_interp_spline = interpolate.splev(x_data_interp, f_interp_spline, der=0)

    # perform cubic spline smoothing
    f_smooth_spline = interpolate.splrep(x_data_nonan, y_data_nonan, s=15, k=3)
    y_smooth_spline = interpolate.splev(x_data_interp, f_smooth_spline, der=0)
    
    # calculate the max DT during eclipse (not extended eclipse)
    origin = xr.DataArray(temp.values, coords=[temp.time], dims=['time'])
    # lineal = xr.DataArray(y_lineal, coords=[time_interp], dims=['time'])
    # interp = xr.DataArray(y_interp_spline, coords=[time_interp], dims=['time'])
    smooth = xr.DataArray(y_smooth_spline, coords=[time_interp], dims=['time'])

    # dlineal = (lineal-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()
    # dinterp = (interp-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()
    dsmooth = (smooth-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()

    round_float = lambda z: round(float(z.values), 2)

    # df.loc['DTmax 3hrs lineal', col] = round_float(dlineal)
    # df.loc['DTmax 3hrs spline interp', col] = round_float(dinterp)
    # df.loc['DTmax 3hrs spline smooth', col] = round_float(dsmooth)

    y[i] = round_float(dsmooth)

    # calculate the time at which max DT occurs
    # calc_time = lambda x: x.time[(x-origin).argmax()].values
    # to_str = lambda t: pd.to_datetime(t).strftime('%H:%M:%S')

    # df.loc['Argmax 3hrs lineal', col] = to_str(calc_time(lineal))
    # df.loc['Argmax 3hrs spline interp', col] = to_str(calc_time(interp))
    # df.loc['Argmax 3hrs spline smooth', col] = to_str(calc_time(smooth))

    # # calculate eclipse DT
    # temp_ecl = temp.sel(time='2021-12-04 ' + df.loc['Maximum eclipse', col][:l], method='nearest')
    # time_ecl = temp_ecl.time
    # df.loc['DTecl 3hrs lineal', col] = round_float((lineal-origin).sel(time=time_ecl))
    # df.loc['DTecl 3hrs spline interp', col] = round_float((interp-origin).sel(time=time_ecl))
    # df.loc['DTecl 3hrs spline smooth', col] = round_float((smooth-origin).sel(time=time_ecl))
    # df.loc['Discrete time eclipse', col] = to_str(time_ecl.values)

# plot the data
fig = plt.figure(figsize=(12,6))

# # plot interp curves
# plt.plot(time_interp, y_lineal, lw=0.8, c='g')
# plt.plot(time_interp, y_interp_spline, lw=0.8, c='brown')

# # plot smooth curve
# plt.plot(time_interp, y_smooth_spline, lw=0.8, c='b')

# # plot original temperature time series
# plt.plot(temp.time, temp.values, lw=0.8, c='k')

plt.plot(x, y,  lw=0.8, c='b')
plt.scatter(x, y,  c='b')

# # shrink current axis's height by 10% on the bottom
# box = plt.gca().get_position()
# plt.gca().set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

# # print legend with DT for each technique
# plt.legend(['Maximum eclipse', 
#             f'lineal\nDT={dlineal.values:.2f}', 
#             f'Cubic spline interp (s=0, k=3)\nDT={dinterp.values:.2f}', 
#             f'Cubic spline smooth (s=15, k=3)\nDT={dsmooth.values:.2f}', 
#             'Original'], 
#         loc='upper center', 
#         bbox_to_anchor=(0.5, -0.15),
#         fancybox=False, 
#         shadow=False,
#         frameon=False,
#         ncol=5)

# rest of plotting routine
plt.xlabel('Extension (min)')
plt.ylabel('Temperature drop (deg C)')
plt.grid(ls='--', lw='0.2', c='grey')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().yaxis.set_ticks_position('left')
plt.gca().xaxis.set_ticks_position('bottom')
# plt.title(f"Name: {col}",
#         loc='left',
#         fontdict = {'fontsize':11})
# save figure
# plt.savefig('../data/interp_time_series_with_eclipse/'+code+'.png', dpi=350)
plt.show()