import sys
from datetime import datetime
import matplotlib.pyplot as plt

sys.path.append('../../processing/')
from processing.aws import AWS, AWSWiscReader

# select the filepath with data from wisc aws
filepath = '../../../antarctica_data/wisc_aws_q10_2021_12/jas202112q10.txt'

# read the file to aws station object
aws_reader = AWSWiscReader()
aws = aws_reader.read_aws(filepath)

# get the original time series
temp = aws.atmvar['T2m']

# select period near eclipse
temp_sel = temp.sel(time=slice('2021-12-03 00:00:00', '2021-12-04 20:00:00'))

# define the eclipse timestamps for jas station
time_pre_eclipse = datetime(2021, 12, 4, 6, 35, 52) # 06:35:52.8
time_eclipse = datetime(2021, 12, 4, 7, 29, 40) # 07:29:40
time_pos_eclipse = datetime(2021, 12, 4, 8, 24, 46, 2) # 08:24:46.2

# plot the data
fig = plt.figure(figsize=(12,6))

# red rectangle during eclipse
plt.gca().axvspan(time_pre_eclipse, time_pos_eclipse, alpha=0.2, color='red')

# red vertical line in eclipse 
plt.axvline(time_eclipse, lw=0.8, c='r')

# plot original temperature time series
plt.plot(temp_sel.time, temp_sel.values, lw=0.8, c='k')
plt.xlabel('Time (UTC)')
plt.ylabel('Temperature (deg C)')
plt.grid(ls='--', lw='0.2', c='grey')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().yaxis.set_ticks_position('left')
plt.gca().xaxis.set_ticks_position('bottom')
plt.title(f"Name: {aws.name}    Code: {aws.code}    Lat: {aws.lat}    Lon: {aws.lon}    Elev: {aws.elev}")
plt.show()
