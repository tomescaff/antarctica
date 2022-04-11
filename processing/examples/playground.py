import pandas as pd
import numpy as np
import xarray as xr
import re 
import sys

sys.path.append('../')

from processing.aws import AWS, AWSGUReader, AWSHalleyReader, AWSArgusReader, AWSNOAAReader, AWSNZReader, AWSGUReader

# basepath = '../../../antarctica_data/data_extra/'
# filename = 'halley_2021-12-04.txt'
# filepath = basepath + filename

# aws = AWSHalleyReader().read_aws(filepath)

# basepath = '../../../antarctica_data/data_extra/'
# filename = 'aws_1minute_20211201-20211206_DOME_ARGUS_Australia.csv'
# filepath = basepath + filename

# aws = AWSArgusReader().read_aws(filepath)

# basepath = '../../../antarctica_data/data_extra/'
# filename = 'met_spo_insitu_1_obop_minute_2021_12.txt'
# filepath = basepath + filename

# aws = AWSNOAAReader().read_aws(filepath)

# basepath = '../../../antarctica_data/nz/'
# filename = 'HD01D_Data_300000_55510079157.txt'
# filepath = basepath + filename

# aws = AWSNZReader().read_aws(filepath)

basepath = '../../../antarctica_data/GU/'
filename = 'data_5sec_con_nuevo_sensor.txt'
filepath = basepath + filename

aws = AWSGUReader().read_aws(filepath)
