import glob
import sys
import pandas as pd

sys.path.append('../')
from processing.aws import AWS, AWSWiscReader

def to_num_lat(str_lat):
    mult = -1 if str_lat[-1] == 'S' else 1
    return float(str_lat[:-1])*mult

def to_num_lon(str_lon):
    mult = -1 if str_lon[-1] == 'W' else 1
    return float(str_lon[:-1])*mult

def to_num_elev(str_elev):
    return float(str_elev[:-1])


filepaths = sorted(glob.glob('../../data/wisc_aws_q10_2021_12/*.txt'))

aws_reader = AWSWiscReader()
aws_list = [ aws_reader.read_aws(filepath) for filepath in filepaths]

index = ['Station Code', 'Station Name', 'Lat (deg)', 'Lon (deg)', 'Elev (m a.s.l.)', 'Institution', 'Var Code', 'Var Name', 'Var Height (m a.g.l.)']

df = pd.DataFrame(index = index)

for aws in aws_list:
    
    code = aws.code + '_Temp'
    stn_code = aws.code
    stn_name = aws.name
    str_lat = aws.lat
    str_lon = aws.lon
    str_elev = aws.elev
    institution = 'AMRC-UW'
    var_code = 'Temp'
    var_name = 'Air Temperature'
    var_hgt = -9999

    num_lat = to_num_lat(str_lat)
    num_lon = to_num_lon(str_lon)
    num_elev = to_num_elev(str_elev)

    df[code] = [stn_code, stn_name, num_lat, num_lon, num_elev, institution, var_code, var_name, var_hgt]

df.index.name = 'Code'
df.to_csv('../data/table_wisc.csv', sep=';')


df2 = pd.read_csv('../data/table_wisc.csv', sep=';', index_col=0)