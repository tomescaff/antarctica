import pandas as pd
import xarray as xr
import re

import sys
sys.path.append('../')

from processing.aws import AWS, AWSHalleyReader

basepath = '../../data/data_extra/'
filename = 'halley_2021-12-04.txt'
filepath = basepath + filename

aws = AWSHalleyReader().read_aws(filepath)



