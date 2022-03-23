import pandas as pd
import xarray as xr
import re 
import sys
sys.path.append('../')

from processing.aws import AWS, AWSHalleyReader, AWSArgusReader, AWSNOAAReader

basepath = '../../data/data_extra/'
filename = 'halley_2021-12-04.txt'
filepath = basepath + filename

aws = AWSHalleyReader().read_aws(filepath)

basepath = '../../data/data_extra/'
filename = 'aws_1minute_20211201-20211206_DOME_ARGUS_Australia.csv'
filepath = basepath + filename

aws = AWSArgusReader().read_aws(filepath)

basepath = '../../data/data_extra/'
filename = 'met_spo_insitu_1_obop_minute_2021_12.txt'
filepath = basepath + filename

aws = AWSNOAAReader().read_aws(filepath)




