#!/usr/bin/env python3

from PIL import Image
#from imageio import imread, imwrite
#import numpy as np
import sys

if len(sys.argv)<2:
  print('Usage: <file.dds> [file2.dds] ...')

for infile in sys.argv[1:]:
  if infile.endswith('.dds'):
    img = Image.open(infile)
    # Remove empty nonsense
    # FIXME: This throws off the coordinate system.
    #nonzero_box = img.getbbox()
    #img = img.crop(nonzero_box)
    # Constrain to a 1000px-wide 16:9 box
    max_width = 1000
    max_height = int(1000/(16/9.))
    aspect_ratio = float(img.width) / img.height
    if aspect_ratio > (16/9.):
      width, height = max_width, int(max_width/aspect_ratio)
    else:
      width, height = int(max_height*aspect_ratio), max_height
    img = img.resize((width, height), Image.LANCZOS)
    # Save it
    outfile = infile[:-4]+'.png'
    print(width,height,outfile)
    img.save(outfile)
  else:
    print('Skipping',infile)
