import glob
import sys

sys.path.append('../')
from processing.aws import AWS, AWSReader

filepaths = sorted(glob.glob('../../data/wisc_aws_q10_2021_12/*.txt'))

aws_reader = AWSReader()
aws_list = [ aws_reader.read_aws(filepath) for filepath in filepaths]



