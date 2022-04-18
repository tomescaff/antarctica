import pandas as pd
import glob
import sys

sys.path.append('../')

from processing.aws import AWS, AWSWiscReader, AWSHalleyReader, AWSArgusReader, AWSNOAAReader, AWSNZReader, AWSGUReader, AWSEFMReader

# read header from csv
df_header = pd.read_csv('../../../antarctica_data/processing/antarctica_aws_header_ext_qa_bestparms.csv', index_col=0)

# get columns
columns = df_header.columns.tolist()

# prepare index for data table
index = pd.date_range('2021-12-03 00:00:00', '2021-12-04 23:50:00', freq='10min')
df_data = pd.DataFrame(index = index, columns=columns)

# add data from wisconsin aws
filepaths = sorted(glob.glob('../../../antarctica_data/wisc_aws_q10_2021_12/*.txt'))
aws_reader = AWSWiscReader()
aws_list = [aws_reader.read_aws(filepath) for filepath in filepaths]

for aws in aws_list:
    code = aws.code + '_Temp'
    series = aws.atmvar['T2m'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
    data = series.values
    time = series.time.values
    df_data.loc[time,code]=data

# add data from BOM aws
filepaths = sorted(glob.glob('../../../antarctica_data/nz/*.txt'))
stn_codes = ['DAV', 'MAW', 'MAI', 'CAS', 'DWW']

aws_reader = AWSNZReader()
aws_list = [aws_reader.read_aws(filepath) for filepath in filepaths]

for aws, stn_code in zip(aws_list, stn_codes):
    code = stn_code + '_Temp'
    series = aws.atmvar['Air Temperature in degrees Celsius'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
    data = series.values
    time = series.time.values
    df_data.loc[time,code]=data

# add data from BAS aws
filepaths = sorted(glob.glob('../../../antarctica_data/data_extra/*2021-12-04.txt'))
stn_codes = ['HAL', 'ROT']

aws_reader = AWSHalleyReader()
aws_list = [aws_reader.read_aws(filepath) for filepath in filepaths]

for aws, stn_code in zip(aws_list, stn_codes):
    code = stn_code + '_Temp_ext_Avg'
    series = aws.atmvar['Temp_ext_Avg'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
    data = series.values
    time = series.time.values
    df_data.loc[time,code]=data

    code = stn_code + '_Temp_hmp_Avg'
    series = aws.atmvar['Temp_hmp_Avg'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
    data = series.values
    time = series.time.values
    df_data.loc[time,code]=data

# add data from NOAA aws
basepath = '../../../antarctica_data/data_extra/'
filename = 'met_spo_insitu_1_obop_minute_2021_12.txt'
filepath = basepath + filename
aws = AWSNOAAReader().read_aws(filepath)

code = 'SPO_Temp_2m'
series = aws.atmvar['TEMPERATURE at 2 Meters'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

code = 'SPO_Temp_10m'
series = aws.atmvar['TEMPERATURE at 10 Meters'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

code = 'SPO_Temp_27m'
series = aws.atmvar['TEMPERATURE at Tower Top'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

# add data from AAP aws
basepath = '../../../antarctica_data/data_extra/'
filename = 'aws_1minute_20211201-20211206_DOME_ARGUS_Australia.csv'
filepath = basepath + filename
aws = AWSArgusReader().read_aws(filepath)

code = 'DOM_Temp_1m'
series = aws.atmvar['AIR_TEMPERATURE_1M'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

code = 'DOM_Temp_2m'
series = aws.atmvar['AIR_TEMPERATURE_2M'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

code = 'DOM_Temp_4m'
series = aws.atmvar['AIR_TEMPERATURE_4M'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

# add data from GU aws
basepath = '../../../antarctica_data/GU/'
filename = 'data_5sec_con_nuevo_sensor.txt'
filepath = basepath + filename
aws = AWSGUReader().read_aws(filepath)

code = 'GU_Temp'
series = aws.atmvar['T2m'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

# add data from EFM aws
basepath = '../../../antarctica_data/EFM/'
filename = 'estacion_EFM_3_4_dic_2021.csv'
filepath = basepath + filename
aws = AWSEFMReader().read_aws(filepath)

code = 'EFM_Temp'
series = aws.atmvar['T2m'].sel(time=slice('2021-12-03 00:00:00', '2021-12-04 23:50:00'))
data = series.values
time = series.time.values
df_data.loc[time,code]=data

# create table with data
df_data = df_data.round(2)
df_data = df_data.fillna(value = -9999)
df_data.to_csv('../../../antarctica_data/processing/antarctica_aws_data.csv', sep=',', float_format='%.2f')

# create table with data and metadata
df_data = pd.read_csv('../../../antarctica_data/processing/antarctica_aws_data.csv', index_col=0)
df_data = df_data.replace(-9999.00, '-9999')
df = df_header.append(df_data)
df.index.name = 'Code'
df.to_csv('../../../antarctica_data/output/antarctica_aws.csv', sep=',')


