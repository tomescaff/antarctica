import pandas as pd
import xarray as xr
import re

class AWS:
    '''This class represents an Automatic Weather Station and its time series'''

    def __init__(self, name, code, lat, lon, elev):
        self.name = name
        self.code = code
        self.lat = lat
        self.lon = lon
        self.elev = elev 
        self.atmvar = dict()

    def add_atmvar(self, name, time_series_dataarray):
        self.atmvar[name] = time_series_dataarray


class AWSWriter:
    '''This class is responsible for saving a group of AWS as a .csv file'''

    pass

class AWSWiscReader:
    '''This class reads an AWS from a .txt file from wisc data'''

    def read_aws(self, filepath):
        aws = self.read_metadata(filepath)
        da = self.read_time_series(filepath)
        aws.add_atmvar('T2m', da)
        return aws

    def read_metadata(self, filepath):
        with open(filepath) as f:
            firstline = f.readline().rstrip()
            first_match_obj = re.match( r'Year: (.*) Month: (.*) ID: (.*) ARGOS: (.*) Name: (.*)', firstline)

            secondline = f.readline().rstrip()
            second_match_obj = re.match( r'Lat: (.*) Lon: (.*) Elev: (.*)', secondline)
        return AWS( first_match_obj.group(5).strip(),
                    first_match_obj.group(3).strip(),
                    second_match_obj.group(1).strip(),
                    second_match_obj.group(2).strip(),
                    second_match_obj.group(3).strip(),
                  )

    def read_time_series(self, filepath):
        df = pd.read_csv(filepath, skiprows=2, header=None, sep='\s+', na_values=444.0)
        temp = df[5]
        time = pd.date_range("2021-12-01", "2021-12-31 23:50:00", freq="10min")
        da = xr.DataArray(temp, coords=[time], dims=['time'])
        return da

class AWSHalleyReader:
    '''This class reads an AWS from a .txt file from halley or rothera station'''

    def read_aws(self, filepath):
        aws = AWS(None, None, None, None, None)
        varnames = ['Temp_ext_Avg', 'Temp_hmp_Avg', 'Temp_box_Avg']
        for varname in varnames:
            da_min = self.read_time_series(filepath, varname)
            da = self.resample_time_series(da_min)
            aws.add_atmvar(varname, da)
        return aws
        
    def read_time_series(self, filepath, varname):
        df = pd.read_csv(filepath, sep=',')
        time = pd.to_datetime(df['TIMESTAMP'])
        data = df[varname]
        da_min = xr.DataArray(data, coords=[time], dims='time')
        return da_min

    def resample_time_series(self, da_min):
        da = da_min.resample(time='10min', closed='right', label='right').mean()[1:-1]
        return da