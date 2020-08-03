#!/usr/bin/env python3

from copy import deepcopy
import os
import re
import sys

from parse_vc import flatten_name
from fsm import FSM, FSMError
from enum import Enum

AUGMENT_DEFAULTS = {
  'fragment_x': 0,
  'fragment_y': 0,
  'fragment': 0,
  'skulls': [],
  'map_x': 0,
  'map_y': 0,
  'map_w': 1,
  'map_h': 1,
  'req_unlocks': [], 
  'opt_unlocks': [], 
  'enemies': [], 
}

class MapParser():
  def __init__(self, file=None):
    self.data = {}
    if file is not None:
      self.parse_map(file)

  def parse_line(self, line):
    if len(line)==0 or line[0]=='#':
      return
    lhs,rhs = line.split('=')

    lhs_parts = lhs.split('.')
    target = self.data
    for part in lhs_parts[:-1]:
      name_and_index = part.split('[')
      name = name_and_index[0]
      if len(name_and_index)==1:
        if name not in target:
          target[name] = {}
        target = target[name]
      else:
        index = int(name_and_index[1][:-1]) # strip trailing ']'
        if name not in target:
          target[name] = []
        target = target[name]
        target.extend([dict() for _ in range(len(target),index+1)])
        target = target[index]
    target[lhs_parts[-1]] = rhs

  def parse_map(self, file):
    while True:
      rawline = file.readline()
      if rawline=='':
        return self.data
      line = rawline.strip()
      self.parse_line(line)

def parse_map(file):
  return MapParser(file).data

def augment_mission(mission, data):
  mission.update(deepcopy(AUGMENT_DEFAULTS))

  mission['map_x'] = float(data['border00']['x'])
  mission['map_y'] = float(data['border00']['y'])
  mission['map_w'] = float(data['border11']['x']) - mission['map_x']
  mission['map_h'] = float(data['border11']['y']) - mission['map_y']
  if 'scriptdata' in data:
    for script in data['scriptdata']:
      # info fragment
      if script['template']=='VoidCrusadeIntel':
        for param in script['params']:
          if param['name']=='Intel':
            mission['fragment'] = True
            x,y = [float(_) for _ in param['pos'].split(';')]
            mission['fragment_x'] = x
            mission['fragment_y'] = y
      # servo skull
      elif script['template']=='VC_Servoskull':
        for param in script['params']:
          if param['name']=='SpawnPoint':
            # These are formatted bizarrely, e.g.:
            #   scriptdata[7].params[2].[0]pos=439.0032;-673.5509
            for k,v in param.items():
              if k.endswith('pos'):
                mission['skulls'].append([float(_) for _ in v.split(';')])
  # enemies
  for enemy in data['soldiergroup']:
    mission['enemies'].append([float(_) for _ in enemy['position'].split(';')])


if __name__=='__main__':
  with open(sys.argv[1]) as f:
    d = MapParser(f).data
  print(len(d))
  print(d.keys())
  print(d['border00']['x'])
  print(d['scriptdata'][5]['params'][1]['pos'])
