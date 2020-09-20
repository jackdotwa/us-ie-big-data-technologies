#!/usr/bin/env python3

import sys

def read_mapper_output(file):
    for line in file:        
        yield line.strip().split(' ')


for vec in read_mapper_output(sys.stdin):
    word = vec[0]
    count = sum(int(number) for number in vec[1:])
    print('{} {}'.format(word, count))
