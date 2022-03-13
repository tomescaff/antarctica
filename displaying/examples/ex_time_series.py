import sys

sys.path.append('../../processing/')
from processing.aws import AWS, AWSReader

filepath = '../../data/wisc_aws_q10_2021_12/jas202112q10.txt'
#filepath = '../../data/wisc_aws_q10_2021_12/kth202112q10.txt'

aws_reader = AWSReader()
aws = aws_reader.read_aws(filepath)

temp = aws.real_time_series

temp_sel = temp.sel(time=slice('2021-12-03 00:00:00', '2021-12-04 20:00:00'))

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(12,6))
plt.plot(temp_sel.time, temp_sel.values, lw=0.8, c='b')
plt.xlabel('Time (UTC)')
plt.ylabel('Temperature (deg C)')
plt.grid(ls='--', lw='0.2', c='grey')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().yaxis.set_ticks_position('left')
plt.gca().xaxis.set_ticks_position('bottom')
plt.title(f"Name: {aws.name}    Code: {aws.code}    Lat: {aws.lat}    Lon: {aws.lon}    Elev: {aws.elev}")
plt.show()
