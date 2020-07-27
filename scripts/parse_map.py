#!/usr/bin/env python3

import os
import re

from parse_vc import flatten_name
from fsm import FSM
from enum import Enum

_S = Enum('_S','TOP VC_INTEL')

def set_script_index(M,D):
  D['script_index'] = int(M[0])
  return _S.VC_INTEL
def set_position(M,D):
  if int(M[0])==D['script_index']:
    D['x'],D['y'] = float(M[1]),float(M[2])
    return None
  return _S.TOP
def conditional_exit_vc_intel(M,D):
  if int(M[0])==D['script_index']:
    return None
  return _S.TOP

machine = {
  _S.TOP: [
    (r'scriptdata\[(\d+)\]\.template=VoidCrusadeIntel', set_script_index),
    (r'.*', None)
  ],
  _S.VC_INTEL: [
    (r'scriptdata\[(\d+)\]\.pos=([^;]*);(.*)', set_position),
    (r'.*', lambda M,D: _S.TOP)
  ],
}


def parse_map(file):
  fsm = FSM(_S, _S.TOP, [_S.TOP], machine)
  fsm.reset()
  fsm.data = { 'script_index':-1 }
  #fsm.tracing(1)
  fsm.parse(file)
  if fsm.data['script_index']<0:
    return None
  else:
    return {k:v for k,v in fsm.data.items() if k in ['x','y']}


def recursively_parse_maps(map_directory):
  # The map directory structure is:
  # .
  #  \-- Ivory
  #     basicmission_1.cfg
  #     basicmission_2.cfg
  #     ...
  #  \-- Ebony
  #     ...

  for vc_directory in os.listdir(map_directory):
    vc_dir = os.path.join(map_directory, vc_directory)
    print(vc_dir)
    for map_name in os.listdir(vc_dir):
      if '.cfg' in map_name:
        with open(os.path.join(vc_dir, map_name)) as f:
          v = parse_map(f)
          if v is not None:
            print(flatten_name(map_name), v['x'], v['y'])
