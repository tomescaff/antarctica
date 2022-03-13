import pandas as pd
import xarray as xr
import re

basepath = '../../data/wisc_aws_q10_2021_12/'
filename = 'ag4202112q10.txt'
filepath = basepath + filename

df = pd.read_csv(filepath, skiprows=2, header=None, sep='\s+', na_values=444.0)
temp = df[5]
time = pd.date_range("2021-12-01", "2021-12-31 23:50:00", freq="10min")
da = xr.DataArray(temp, coords=[time], dims=['time'])

with open(filepath) as f:
    firstline = f.readline().rstrip()
    first_match_obj = re.match( r'Year: (.*)  Month: (.*)  ID: (.*)  ARGOS:  (.*)  Name: (.*)', firstline)
    
    secondline = f.readline().rstrip()
    second_match_obj = re.match( r'Lat: (.*)  Lon:  (.*)  Elev: (.*)', secondline)