import sys
import datetime as dt
import numpy as np
import xarray as xr
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt

sys.path.append('../../processing/examples/')
sys.path.append('../../processing/')

from subsample_data_eclipse import data

# select aws code
code = 'jas' # [jas, kth, byd, lda]

# get data from processing dir
aws = data[code]['aws']
ini = dt.datetime.fromisoformat(data[code]['ini_eclipse'])
mae = dt.datetime.fromisoformat(data[code]['max_eclipse'])
end = dt.datetime.fromisoformat(data[code]['end_eclipse'])
temp = aws.atmvar['T2m']

# artificial extension of end time eclipse
ext = end + dt.timedelta(0,60*30)

# select period of time series near eclipse
temp_sel = temp.sel(time=slice('2021-12-03 00:00:00', '2021-12-04 20:00:00'))

# remove data during eclipse
temp_sel_mod = temp_sel.where((temp_sel.time < np.datetime64(ini)) | (temp_sel.time > np.datetime64(ext)))

# starting interpolation

# define x and y data
y_data = temp_sel_mod.values
x_data = np.arange(temp_sel_mod.time.values.size)

# remove nans from x and y data where y is nan
x_data_nonan = x_data[~np.isnan(y_data)]
y_data_nonan = y_data[~np.isnan(y_data)]

# perform linear interpolation
f_lineal = interp1d(x_data_nonan, y_data_nonan)
y_lineal = f_lineal(x_data)

# perform cubic spline interpolation
f_interp_spline = interpolate.splrep(x_data_nonan, y_data_nonan, s=0, k=3)
y_interp_spline = interpolate.splev(x_data, f_interp_spline, der=0)

# perform cubic spline smoothing
f_smooth_spline = interpolate.splrep(x_data_nonan, y_data_nonan, s=15, k=3)
y_smooth_spline = interpolate.splev(x_data, f_smooth_spline, der=0)

# calculate the max DT during eclipse (not extended eclipse)
origin = xr.DataArray(temp_sel.values, coords=[temp_sel_mod.time], dims=['time'])
lineal = xr.DataArray(y_lineal, coords=[temp_sel_mod.time], dims=['time'])
interp = xr.DataArray(y_interp_spline, coords=[temp_sel_mod.time], dims=['time'])
smooth = xr.DataArray(y_smooth_spline, coords=[temp_sel_mod.time], dims=['time'])

dlineal = (lineal-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()
dinterp = (interp-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()
dsmooth = (smooth-origin).where(((origin.time >= np.datetime64(ini)) & (origin.time <= np.datetime64(end))), drop=True).max()

# plot the data
fig = plt.figure(figsize=(12,6))

# plot red rectangle during eclipse
plt.gca().axvspan(ini, end, alpha=0.1, color='red')

# plot another red rectangle during the extended eclipse
plt.gca().axvspan(ini, ext, alpha=0.1, color='red')

# plot red vertical line at maximum eclipse
plt.axvline(mae, lw=0.8, c='r')

# plot interp curves
plt.plot(temp_sel_mod.time, y_lineal, lw=0.8, c='g')
plt.plot(temp_sel_mod.time, y_interp_spline, lw=0.8, c='brown')

# plot smooth curve
plt.plot(temp_sel_mod.time, y_smooth_spline, lw=0.8, c='b')

# plot original temperature time series
plt.plot(temp_sel.time, temp_sel.values, lw=0.8, c='k')

# shrink current axis's height by 10% on the bottom
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

# print legend with DT for each technique
plt.legend(['Maximum eclipse', 
            f'lineal\nDT={dlineal.values:.2f}', 
            f'Cubic spline interp (s=0, k=3)\nDT={dinterp.values:.2f}', 
            f'Cubic spline smooth (s=15, k=3)\nDT={dsmooth.values:.2f}', 
            'Original'], 
           loc='upper center', 
           bbox_to_anchor=(0.5, -0.15),
           fancybox=False, 
           shadow=False,
           frameon=False,
           ncol=5)

# rest of plotting routine
plt.xlabel('Time (UTC)')
plt.ylabel('Temperature (deg C)')
plt.grid(ls='--', lw='0.2', c='grey')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().yaxis.set_ticks_position('left')
plt.gca().xaxis.set_ticks_position('bottom')
plt.title(f"Name: {aws.name}    Code: {aws.code}    Lat: {aws.lat}    Lon: {aws.lon}    Elev: {aws.elev}",
          loc='left',
          fontdict = {'fontsize':11})
# save figure
plt.savefig('../../../antarctica_data/displaying/interp_time_series_with_eclipse/'+code+'.png', dpi=350)
plt.show()