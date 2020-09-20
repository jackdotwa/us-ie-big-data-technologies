#!/usr/bin/python3

import sys
import re

pattern = re.compile("^[a-z]+$")
for line in sys.stdin: 
    line = line.strip()
    tokens = line.split()
    for token in tokens:
        lowercaseword = token.lower()
        if pattern.match(lowercaseword):
            print('{} 1'.format(lowercaseword))
