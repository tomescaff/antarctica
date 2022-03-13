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

    def set_real_time_series(self, time_series_dataarray):
        self.real_time_series = time_series_dataarray

    def set_mod_time_series(self, time_series_dataarray):
        self.mod_time_series = time_series_dataarray

class AWSWriter:
    '''This class is responsible for saving a group of AWS as a .csv file'''

    pass

class AWSReader:
    '''This class reads an AWS from a .txt file from wisc data'''

    def read_aws(self, filepath):
        aws = self.read_metadata(filepath)
        df = self.read_time_series(filepath)
        aws.set_real_time_series(df)
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
    