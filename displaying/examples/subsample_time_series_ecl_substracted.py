import sys
import datetime as dt
import numpy as np
sys.path.append('../../processing/examples/')
sys.path.append('../../processing/')

from subsample_data_eclipse import data
import matplotlib.pyplot as plt

# select aws code
code = 'jas' # [jas, kth, byd, lda]

# get data from processing dir
aws = data[code]['aws']
ini = dt.datetime.fromisoformat(data[code]['ini_eclipse'])
mae = dt.datetime.fromisoformat(data[code]['max_eclipse'])
end = dt.datetime.fromisoformat(data[code]['end_eclipse'])
temp = aws.real_time_series

# artificial extension of end time eclipse
ext = end + dt.timedelta(0,60*30)

# select period of time series near eclipse
temp_sel = temp.sel(time=slice('2021-12-03 00:00:00', '2021-12-04 20:00:00'))

# remove data during eclipse
temp_sel_mod = temp_sel.where((temp_sel.time.values < np.datetime64(ini)) | (temp_sel.time.values > np.datetime64(ext)))

# plot the data
fig = plt.figure(figsize=(12,6))

# plot red rectangle during eclipse
plt.gca().axvspan(ini, end, alpha=0.1, color='red')

# plot another red rectangle during the extended eclipse
plt.gca().axvspan(ini, ext, alpha=0.1, color='red')

# plot red vertical line at maximum eclipse
plt.axvline(mae, lw=0.8, c='r')

# plot original temperature time series without eclipse time lapse
plt.plot(temp_sel_mod.time, temp_sel_mod.values, lw=0.8, c='k')

# shrink current axis's height by 10% on the bottom
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

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
plt.savefig('../data/orig_time_series_with_ecl_substracted/'+code+'.png', dpi=350)
plt.show()