#!/usr/bin/env python3

from copy import deepcopy
import os
import re
import sys

from parse_vc import flatten_name
from fsm import FSM, FSMError
from enum import Enum

AUGMENT_DEFAULTS = {
  # Temporary
  'map_unlock_flags': [], 
  'has_dataslate': False,
  'needs_dataslate': True,

  # Permanent
  'map_x': 0,
  'map_y': 0,
  'map_w': 1,
  'map_h': 1,
  # Markers
  # [] means the mission doesn't have this marker
  # [['string',x,y], ...] means 1+ markers exist, the string describes it
  'objectives': [],
  'fragments': [],
  'skulls': [],
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

def get_multiple_coords(subsection, name=None, type='Dummy'):
  # For pulling apart coordinates in the form:
  #   missiondata[i].params[j].pos=x;y
  # subsection is a list, typically `Xdata[X].params`
  obj_lists = [get_coords(subsection, name=param['name'], type=type)
               for param in subsection
               if (re.match(name+r'[0-9]$', param['name']) is not None)]
  objs = [pair for coords in obj_lists for pair in coords]
  return objs

def get_coords(subsection, name=None, type='DummyList'):
  # For pulling apart coordinates in the form:
  #   missiondata[i].params[j].[k]pos=x;y
  # subsection is a list, typically `Xdata[X].params`
  for param in subsection:
    if param['type']==type:
      if name is None or param['name']==name:
        coords = [[float(_) for _ in v.split(';')]
                  for k,v in param.items() if k.endswith('pos')]
        return coords
  raise Exception('Mission coordinates')

def get_objective_locations(data):
  mission_type = data['missiondata'][0]['template']
  mission_params = data['missiondata'][0]['params']
  if mission_type=='Assassination': # Azure/bonusmission3
    objs = get_coords(mission_params, name='TargetLocation')
  elif mission_type=='Bunkerbusting': # Ecru/bonusmission2
    batteries = get_coords(mission_params, name='LaserBatteryLocation')
    bunker = get_coords(mission_params, name='BunkerLocation')
    objs = batteries + bunker
  elif mission_type=='Datahunt': # Azure/bonusmission2
    objs = get_multiple_coords(mission_params, name='Clue_')
  elif mission_type=='Forcefield': # Amber/secretmissionalpha
    objs = get_multiple_coords(mission_params, name='Clue_')
  elif mission_type=='GeneratorDestroy': # Ebony/secretmissionbeta
    objs = get_multiple_coords(mission_params, name='Object ')
  elif mission_type=='HotPursuit': # Amber/mission11
    # The target actually runs a pre-defined route, but we're just going to put
    # a marker at the start location.
    for param in mission_params:
      if param['name']=='Route':
        objs = [[float(_) for _ in param['point[0]'].split(';')]]
  elif mission_type=='Hunt': # Ivory/endmission3
    objs = get_coords(mission_params, name='TargetLocation')
  elif mission_type=='Incursion': # Zircon/bonusmission3
    objs = get_multiple_coords(mission_params, name='WarpGate')
  elif mission_type=='IntelPursuit': # Amber/bonusmission3
    survivor = get_coords(mission_params, name='Ally', type='Dummy')
    intel = get_coords(mission_params, name='Intel', type='Dummy')
    objs = survivor + intel
  elif mission_type=='NurgleHunt': # Viridian/endmission2
    objs = get_multiple_coords(mission_params, name='Target')
  elif mission_type=='Nurgle_Infestation': # Viridian/secretmissionalpha
    objs = get_coords(mission_params, name='NurgleSiteLocation')
  elif mission_type=='PanicRoom': # Viridian/bonusmission1
    vip = get_coords(mission_params, name='VIP', type='Dummy')
    extraction = get_coords(mission_params, name='Extraction')
    objs = vip + extraction
  elif mission_type=='Purge':
    objs = []
  elif mission_type=='Rescue': # Amber/bonusmission1
    soldiers = get_multiple_coords(mission_params, name='Group')
    evac = get_coords(mission_params, name='EvacuationLocation')
    objs = soldiers + evac
  elif mission_type=='Siege': # Amber/secretmissionbeta
    objs = get_coords(mission_params, name='Fortified_Zone')
  elif (mission_type=='Silencethegun' or
        mission_type=='SilenceTheGun' or
        mission_type=='silencethegun'): # Azure/hiddenmission3
    objs = get_coords(mission_params, name='Gun')
  elif mission_type=='SporocystAssault': # Ecru/endmission1
    objs = get_coords(mission_params, name='TargetLocation')
  elif mission_type=='Tarot_Hunt': # Zircon/endmission2
    objs = get_coords(mission_params, name='TargetLocation')
  elif mission_type=='Tarot_Purge':
    objs = []
  else:
    raise Exception('Unknown mission type: '+str(mission_type))

  # FIXME: don't do this
  objs = [['Objective',*_] for _ in objs]
  print(objs)
  return objs

#  'map_unlock_flags': [],
#  'has_dataslate': False,
#  'needs_dataslate': True,


def get_unlocks(mission, data):
  unlocks = []
  # FIXME: NYI

  # dataslate terminal
  # dataslate drop
  # stormwatcher
  # intel beacon
  # completion

  return mission

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
            mission['fragments'] = [['Info Fragment'] +
                                    [float(_) for _ in param['pos'].split(';')]]
      # servo skull
      elif script['template']=='VC_Servoskull':
        for param in script['params']:
          if param['name']=='SpawnPoint':
            # These are formatted bizarrely, e.g.:
            #   scriptdata[7].params[2].[0]pos=439.0032;-673.5509
            for k,v in param.items():
              if k.endswith('pos'):
                mission['skulls'].append(['Possible Servoskull Spawn'] +
                                         [float(_) for _ in v.split(';')])
  # mission objectives
  mission['objectives'] = get_objective_locations(data)
  # enemies
  for enemy in data['soldiergroup']:
    mission['enemies'].append([enemy['name']] + 
                              [float(_) for _ in enemy['position'].split(';')])


if __name__=='__main__':
  with open(sys.argv[1]) as f:
    d = MapParser(f).data
  print(len(d))
  print(d.keys())
  print(d['border00']['x'])
  print(d['scriptdata'][5]['params'][1]['pos'])
