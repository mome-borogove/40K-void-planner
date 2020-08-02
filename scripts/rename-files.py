#!/usr/bin/env python3

from parse_vc import flatten_name

mission_names = ['ivory','ebony','ecru','amber','viridian','azure','zircon',
                 'iv','eb','ec','am','vi','az','zi']

import re
import os.path
import sys

# In general, use these on the .dds files.

if len(sys.argv)<2:
  print('Usage: <file> [file2] ...')

for infile in sys.argv[1:]:
  prefix,filename = os.path.split(infile)
  # Strip crusade names
  for pat in mission_names:
    filename = re.sub(r'^'+pat+r'_?', r'', filename)
  filename = flatten_name(filename)
  outfile = os.path.join(prefix,filename)
  print(infile,'=>',outfile)
  os.rename(infile, outfile)
