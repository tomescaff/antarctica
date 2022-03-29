import pandas as pd

df = pd.read_csv('../data/antarctica_aws_header.csv', index_col=0)

basestr = "http://xjubier.free.fr/en/site_pages/SolarEclipseCalculator_xSE_GE.php?Eclipse=+20211204&Lat={}&Lng={}&Alt={}&TZ=%27+0000%27&DST=0&Calc=1&VSOP=1&Mes=0&Lang="

columns = df.columns.tolist()

for col in columns:
    print(col)
    lat = df.loc['Lat (deg)', col]
    lon = df.loc['Lon (deg)', col]
    elev = df.loc['Elev (m a.s.l.)', col]
    print(basestr.format(lat, lon, elev))
    print('')