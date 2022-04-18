import pandas as pd
import xarray as xr
import re
import numpy as np
import datetime as dt

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
        da = da_min.resample(time='10min', closed='right', label='right', skipna=True).mean()[1:-1]
        return da

class AWSArgusReader:
    '''This class reads an AWS from a .txt file from ARGUS Australian station'''

    def read_aws(self, filepath):
        aws = AWS(None, None, None, None, None)
        varnames = ['AIR_TEMPERATURE_1M', 'AIR_TEMPERATURE_2M', 'AIR_TEMPERATURE_4M']
        for varname in varnames:
            da_min = self.read_time_series(filepath, varname)
            da = self.resample_time_series(da_min)
            aws.add_atmvar(varname, da)
        return aws
        
    def read_time_series(self, filepath, varname):
        df = pd.read_csv(filepath, sep=',')
        time = pd.to_datetime(df['OBSERVATION_DATE'])
        data = df[varname].replace(0, np.nan)
        da_min = xr.DataArray(data, coords=[time], dims=['time']).sortby('time')
        return da_min

    def resample_time_series(self, da_min):
        da = da_min.resample(time='10min', closed='right', label='right', skipna=True).mean()[1:-1]
        return da

class AWSNOAAReader:
    '''This class reads an AWS from a .txt file from NOAA data'''

    def read_aws(self, filepath):
        aws = AWS(None, None, None, None, None)
        varnames = ['TEMPERATURE at 2 Meters', 'TEMPERATURE at 10 Meters', 'TEMPERATURE at Tower Top']
        varcolumns = [10, 11, 12]
        for (n, c) in zip(varnames, varcolumns):
            da_min = self.read_time_series(filepath, c)
            da = self.resample_time_series(da_min)
            aws.add_atmvar(n, da)
        return aws
        
    def read_time_series(self, filepath, varcolumn):
        df = pd.read_csv(filepath, header=None, sep='\s+', parse_dates={'datetime':[1,2,3,4,5]})
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y %m %d %H %M')
        time = df['datetime']
        data = df[varcolumn]
        da_min = xr.DataArray(data, coords=[time], dims=['time']).sortby('time')
        return da_min

    def resample_time_series(self, da_min):
        da = da_min.resample(time='10min', closed='right', label='right', skipna=True).mean()[1:-1]
        return da

class AWSNZReader:
    '''This class reads an AWS from a .txt file from NZ data'''

    def read_aws(self, filepath):
        aws = AWS(None, None, None, None, None)
        varnames = ['Air Temperature in degrees Celsius']
        for name in varnames:
            da_min = self.read_time_series(filepath, name)
            da = self.resample_time_series(da_min)
            aws.add_atmvar(name, da)
        return aws
        
    def read_time_series(self, filepath, name):
        parsedict = {'datetime': [' Year Month Day Hour Minutes in YYYY.2',
                          'MM.2',
                          'DD.2',
                          'HH24.2',
                          'MI format in Universal coordinated time']}
        df = pd.read_csv(filepath, sep=',', low_memory=False, parse_dates=parsedict)
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y %m %d %H %M')
        time = df['datetime']
        data_str = df[name]
        data = data_str.apply(lambda x: float(x.strip()) if x.strip() != '' else np.nan)
        da_min = xr.DataArray(data, coords=[time], dims=['time']).sortby('time')
        return da_min

    def resample_time_series(self, da_min):
        da = da_min.resample(time='10min', closed='right', label='right', skipna=True).mean()[1:-1]
        return da

class AWSGUReader:
    '''This class read an AWS from data_5sec_con_nuevo_sensor.txt file from Glaciar Union data'''

    def read_aws(self, filepath):
        aws = AWS(None, None, None, None, None)
        da_5sec = self.read_time_series(filepath)
        da = self.resample_time_series(da_5sec)
        aws.add_atmvar('T2m', da)
        return aws

    def read_time_series(self, filepath):
        df = pd.read_csv(filepath, sep=',', header = None, skiprows=21207)
        time = pd.date_range('2021-12-02 23:50:00','2021-12-04 12:19:40', freq='5s')
        time = time + dt.timedelta(seconds=60*60*3)
        data = df[6]
        da_5sec = xr.DataArray(data.values, coords=[time.values], dims=['time'])
        return da_5sec

    def resample_time_series(self, da_5sec):
        da = da_5sec.resample(time='10min', closed='right', label='right', skipna=True).mean()[1:-1]
        return da

class AWSEFMReader:
    '''This class read an AWS file from Eduardo Frei Montalva station data'''

    def read_aws(self, filepath):
        aws = AWS(None, None, None, None, None)
        da_min = self.read_time_series(filepath)
        da = self.resample_time_series(da_min)
        aws.add_atmvar('T2m', da)
        return aws

    def read_time_series(self, filepath):
        df = pd.read_csv(filepath, sep = ',', header=None)

        year = df[0].astype(str)
        month = df[1].astype(str)
        day = df[2].apply(lambda x: '0'+str(x))
        hhmm = df[3]

        time_str = year + '-' + month + '-' + day + ' ' + hhmm + ':00'
        time = pd.to_datetime(time_str, format='%Y-%m-%d %H:%M:%S')
        # correct the UTC time
        # time = time + dt.timedelta(seconds=60*60*3)
        data = df[10]
        da_min = xr.DataArray(data, coords=[time], dims=['time'])
        return da_min

    def resample_time_series(self, da_min):
        da = da_min.resample(time='10min', closed='right', label='right', skipna=True).mean()[1:-1]
        return da


    

    