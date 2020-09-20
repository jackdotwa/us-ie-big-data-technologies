#!/usr/bin/env python3

from itertools import groupby
from operator import itemgetter
import sys

def read_mapper_output(file):
    for line in file:        
        yield line.strip().split(' ')
        
        
data = read_mapper_output(sys.stdin)

for key, keygroup in groupby(data, itemgetter(0)):    
    values = ' '.join(sorted(v for k, v in keygroup))    
    print("{} {}".format(key, values))
