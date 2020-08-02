#!/usr/bin/env python3

from copy import deepcopy
import os
import re

from parse_vc import flatten_name
from fsm import FSM
from enum import Enum

AUG_DEFAULTS = {
  'fragment_x': 0,
  'fragment_y': 0,
  'fragment': 0,
  'map_x': 0,
  'map_y': 0,
  'map_w': 1,
  'map_h': 1,
  'req_unlocks': [],
  'opt_unlocks': [],
  'enemies': [],
}

_S = Enum('_S','TOP VC_INTEL')

def set_script_index(M,D):
  D['script_index'] = int(M[0])
  return _S.VC_INTEL

def set_intel_position(M,D):
  if int(M[0])==D['script_index']:
    D['fragment_x'],D['fragment_y'] = float(M[1]),float(M[2])
    D['fragment'] = 1
    return None
  return _S.TOP

def set_map_width(M,D):
  D['map_w'] = float(M[0]) - D['map_x']

def set_map_height(M,D):
  D['map_h'] = float(M[0]) - D['map_y']

def set_map_origin(M,D):
  D['map_'+str.lower(M[0])] = float(M[1])

def add_enemy(M,D):
  x,y = [float(_) for _ in M[0].split(';')]
  #print('Added enemy at ('+str(x)+', '+str(y)+')')
  D['enemies'].append( [x,y] )

def set_property(M,D):
  section,index,property,value = M[0:4]
  if section not in D:
    D[section] = {}
  if index not in D[section]:
    D[section][index] = {}
  D[section][index][property] = value

def conditional_exit_vc_intel(M,D):
  if int(M[0])==D['script_index']:
    return None
  return _S.TOP

machine = {
  _S.TOP: [
    (r'scriptdata\[(\d+)\]\.template=VoidCrusadeIntel', set_script_index),
    #(r'(fragment)\[(\d+)\]\.([^=]*)=(.*)', set_property),
    #(r'(chest)\[(\d+)\]\.([^=]*)=(.*)', set_property),
    (r'soldiergroup\[\d+\]\.position=(.*)', add_enemy),
    (r'border00\.(.)=(.*)', set_map_origin),
    (r'border11\.x=(.*)', set_map_width),
    (r'border11\.y=(.*)', set_map_height),
    (r'.*', None)
  ],
  _S.VC_INTEL: [
    # FIXME: This is incorrect.
    # The correct position is the possition of the Intel Dummy, which is
    # a section of the intel scriptdata entity
    (r'scriptdata\[(\d+)\]\.pos=([^;]*);(.*)', set_intel_position),
    (r'.*', lambda M,D: _S.TOP)
  ],
}


def parse_map(file):
  fsm = FSM(_S, _S.TOP, [_S.TOP], machine)
  fsm.reset()
  fsm.data = deepcopy(AUG_DEFAULTS)
  fsm.data['script_index'] = -1
  #fsm.tracing(1)
  fsm.parse(file)
  #if fsm.data['script_index']<0:
  #  return None
  #else:
  return fsm.data

def get_map_data(file):
  map = parse_map(file)

  return map
