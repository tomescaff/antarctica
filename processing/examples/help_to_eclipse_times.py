import pandas as pd

# read header from csv
df = pd.read_csv('../../../antarctica_data/processing/antarctica_aws_header.csv', index_col=0)

# base URL string
basestr = "http://xjubier.free.fr/en/site_pages/SolarEclipseCalculator_xSE_GE.php?Eclipse=+20211204&Lat={}&Lng={}&Alt={}&TZ=%27+0000%27&DST=0&Calc=1&VSOP=1&Mes=0&Lang="

columns = df.columns.tolist()

# replace and print
for col in columns:
    print(col)
    lat = df.loc['Lat (deg)', col]
    lon = df.loc['Lon (deg)', col]
    elev = df.loc['Elev (m a.s.l.)', col]
    print(basestr.format(lat, lon, elev))
    print('')