import sys

sys.path.append('../')
from processing.aws import AWS, AWSWiscReader

aws_reader = AWSWiscReader()

data = dict()
data['jas'] = {'aws': aws_reader.read_aws('../../../antarctica_data/wisc_aws_q10_2021_12/jas202112q10.txt'),
               'ini_eclipse': "2021-12-04 06:35:53",
               'max_eclipse': "2021-12-04 07:29:41",
               'end_eclipse': "2021-12-04 08:24:46"}

data['kth'] = {'aws': aws_reader.read_aws('../../../antarctica_data/wisc_aws_q10_2021_12/kth202112q10.txt'),
               'ini_eclipse': "2021-12-04 06:57:33",
               'max_eclipse': "2021-12-04 07:48:13",
               'end_eclipse': "2021-12-04 08:39:08"}

data['byd'] = {'aws': aws_reader.read_aws('../../../antarctica_data/wisc_aws_q10_2021_12/byd202112q10.txt'),
               'ini_eclipse': "2021-12-04 07:04:11",
               'max_eclipse': "2021-12-04 07:55:31",
               'end_eclipse': "2021-12-04 08:46:49"}

data['lda'] = {'aws': aws_reader.read_aws('../../../antarctica_data/wisc_aws_q10_2021_12/lda202112q10.txt'),
               'ini_eclipse': "2021-12-04 07:20:28",
               'max_eclipse': "2021-12-04 08:13:53",
               'end_eclipse': "2021-12-04 09:06:22"}