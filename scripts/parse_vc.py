#!/usr/bin/env python3

import re

from copy import deepcopy
from fsm import FSM
from enum import Enum

_S = Enum('_S','TOP VC_NAME VC NODE_NAME NODE')

translation = {
  'faction': {
    'AL_warband': 'alpha_legion',
    'BL_warband': 'black_legion',
    'Eldar_Indoors': 'aeldari',
    'Eldar': 'aeldari',
    'dark_eldar': 'drukhari',
    'khorn': 'khorne',
    'mech_techadept': 'mech',
    'Mech_techadept': 'mech',
    'nurgle_nest': 'nurgle',
    'rebel_army': 'rebel',
    'rebel_chaos_army': 'rebel_chaos',
    'Tyranid': 'tyranid',
    'WB_warband': 'word_bearer',
  },
  'appearance': {
    'Bonus': 'bonus',
    'End': 'end',
    'Hidden': 'covert',
    'Normal': 'normal',
    'Secret': 'secret',
  },
  'objective_type': {
    'Assassination': 'Assassination',
    'Bunkerbusting': 'Bunker busting',
    'Datahunt': 'Data hunt',
    'Forcefield': 'Secure the artifact',
    'GeneratorDestroy': 'Destroy the generator',
    'HotPursuit': 'Hot pursuit',
    'Hunt': 'Hunt',
    'Incursion': 'Daemonic Incursion',
    'IntelPursuit': 'Intel Pursuit',
    'NurgleHunt': 'Nurgle Hunt',
    'Nurgle_Infestation': 'Nurgle Infestation',
    'PanicRoom': 'Panic Room',
    'Purge': 'Purge',
    'Rescue': 'Rescue',
    'Siege': 'Siege',
    'silencethegun': 'Silence the guns',
    'Silencethegun': 'Silence the guns',
    'SporocystAssault': 'Sporocyst Assault',
    'Tarot_Hunt': 'Callous Hunt',
    'Tarot_Purge': 'Infested Station',
  }
}

NODE_DEFAULTS = {
  # Temporary
  'node_unlock_flags': [], # completion unlocks flag, flat list
  'needs_unlock_flags': [], # Unlock flags required to complete this mission.

  # Permanent
  # Apparently there's a single Ivory map without a difficulty setting.
  # It appears as a +1, but it doesn't actually apply the difficulty.
  # So we'll leave it as a 0.
  'difficulty': 0,
  'loot_quality': 0,
  'loot_quantity': 0,
  'loot_rarity': 0,
  'node_unlocks': [],
}

def flatten_name(s):
  # *sigh* Neocore decided not to have any consistency in naming missions.
  # So now I have to fix it.
  s = str.lower(s)
  # Apparently, even though the missions are named End_Mission_01, the
  # *neighbor lists* have them listed as EndMission_01....sometimes. Other
  # times they're End_Mission_01. Yay.
  s = re.sub('_', '', s)
  # Aaaaand some names are partially in Hungarian instead of English.
  # Partially. As in, some of the names are in one language and some in another.
  s = re.sub(r'rejtett', r'hidden', s)
  s = re.sub(r'titkos', r'secret', s)
  s = re.sub(r'bonusz', r'bonus', s)
  # Greek is different in Hungarian. >_<
  s = re.sub(r'alfa', r'alpha', s)
  # Sometimes "basic" is prefixed to normal missions.
  s = re.sub(r'basic', r'', s)
  # They're inconsistent with the use of leading zeros.
  s = re.sub(r'([^0-9])0+', r'\1', s)
  return s

def set_vc_name(M,D):
  name = str.lower(M[0])
  D['vc'] = { 'nodes': {} }
  D['vc']['name'] = name
  D['id_counter'] = 1 # We start at 1 so that we can insert Start at 0
  return _S.VC_NAME
def set_vc_value(key,M,D):
  D['vc'][key] = M[0]
def set_vc_position(M,D):
  x,y = M[0].split(';')
  D['vc']['x'], D['vc']['y'] = 100*float(x)/1920, 100*float(y)/1080
def commit_vc(M,D):
  # FIXME: Currently, the 'Index' field of void crusades is broken.
  # I don't know what Neocore uses this for, but multiple VC's have the same
  # index. So we just hack together a new index value here.
  D['vc']['index'] = len(D['crusades'])
  D['crusades'][D['vc']['name']] = D['vc']
  return _S.TOP

def set_node_name(M,D):
  name = flatten_name(M[0])
  D['node_name'] = name
  # Sometimes values are mysteriously omitted, so we supply some defaults.
  D['node'] = deepcopy(NODE_DEFAULTS)
  D['node']['internal_name'] = name
  D['node']['id'] = D['id_counter']
  D['id_counter'] += 1
  return _S.NODE_NAME

def set_node_value(key,M,D):
  D['node'][key] = M[0]

def set_node_position(M,D):
  x,y = M[0].split(';')
  D['node']['x'], D['node']['y'] = 100*float(x)/1920, 100*float(y)/1080

def translate_value(key, M,D):
  if M[0] not in translation[key]:
    print('missing translation:',M[0])
  D['node'][key] = translation[key].get(M[0],M[0])

def set_neighbors(M,D):
  D['node']['neighbors'] = M[0].split(',')

def set_needs_unlock_flags(M,D):
  D['node']['needs_unlock_flags'] = M[0].split(',')

def set_node_unlock_flags(M,D):
  D['node']['node_unlock_flags'] = M[0].split(',')

def commit_node(M,D):
  D['vc']['nodes'][D['node_name']] = D['node']
  return _S.VC

machine = {
  _S.TOP: [
    (r'([^\s]+)', set_vc_name),
    (r'', None),
  ],
  _S.VC_NAME: [
    (r'{', lambda: _S.VC),
    (r'', None),
  ],
  _S.VC: [
    (r'}', commit_vc),
    (r'StartPoint=(.*)', set_vc_position),
    (r'Index=(.*)', lambda M,D: set_vc_value('index',M,D)),
    (r'.*=.*', None),
    (r'([^\s]+)', set_node_name),
    (r'', None),
  ],
  _S.NODE_NAME: [
    (r'{', lambda: _S.NODE),
    (r'', None),
  ],
  _S.NODE: [
    (r'}', commit_node),
    (r'Type=(.*)', lambda M,D: translate_value('appearance',M,D)),
    (r'Pos=(.*)', set_node_position),
    (r'MonsterSetting=(.*)', lambda M,D: translate_value('faction',M,D)),
    (r'MissionType=(.*)', lambda M,D: translate_value('objective_type',M,D)),
    (r'Neighbours=(.*)', set_neighbors),
    (r'Difficulty=(.*)', lambda M,D: set_node_value('difficulty',M,D)),
    (r'CanSpawnWS=(.*)', lambda M,D: set_node_value('servo',M,D)),
    (r'Unlocks=(.*)', set_needs_unlock_flags),
    (r'AddUnlock=(.*)', set_node_unlock_flags),
    (r'BonusLootQuality=(.*)', lambda M,D: set_node_value('loot_quality',M,D)),
    (r'BonusLootQuantity=(.*)', lambda M,D: set_node_value('loot_quantity',M,D)),
    (r'BonusLootRarity=(.*)', lambda M,D: set_node_value('loot_rarity',M,D)),
    (r'.*=.*', None),
    (r'', None),
  ],
}

def parse_vc(file):
  fsm = FSM(_S, _S.TOP, [_S.TOP], machine)
  fsm.reset()
  fsm.data = {
    'crusades': {},
    'vc_name': '',
    'vc': {},
    'node_name': '',
    'node': {},
  }
  #fsm.tracing(1)
  fsm.parse(file)
  return fsm.data['crusades']

def translate_nodes(nodes):
  name_map = {n['internal_name']:n['id'] for n in nodes.values()}

  for name,node in nodes.items():
    if 'neighbors' in node:
      node['deps'] = [name_map[flatten_name(n)] for n in node['neighbors']]
    else:
      node['deps'] = []

  return nodes

def add_start_node(crusade):
  # Add a false node to represent the starting point
  start_node = deepcopy(NODE_DEFAULTS)
  start_node['internal_name'] = 'start'
  start_node['id'] = 0
  start_node['x'] = crusade['x']
  start_node['y'] = crusade['y']
  start_node['faction'] = 'N/A'
  start_node['objective_type'] = 'N/A'
  start_node['servo'] = 0
  start_node['difficulty'] = 0
  start_node['appearance'] = 'start'
  crusade['nodes']['start'] = start_node
  return crusade['nodes']

def bidirectional_edges(nodes):
  # Initialize from unidirectional lists
  adjacency = { node['id']:set(node['deps']) for node in nodes.values() }
  # Add from bidirectional adjacency list
  for node in nodes.values():
    for neighbor in node['deps']:
      adjacency[neighbor].add(node['id'])
  # verify
  for id,adjs in adjacency.items():
    for adj in adjs:
      assert id in adjacency[adj], '{0} missing from {1} (actual: {2})'.format(id,adj,adjacency[adj])
  # Add from bidirectional adjacency list
  for node in nodes.values():
    node['deps'] = list(adjacency[node['id']])
  return nodes


def get_vc_data(file):
  crusades = parse_vc(file)
  for crusade in crusades.values():
    crusade['nodes'] = add_start_node(crusade)
    crusade['nodes'] = translate_nodes(crusade['nodes'])
    crusade['nodes'] = bidirectional_edges(crusade['nodes'])
  return crusades

if __name__=='__main__':
  with open('voidcrusade.cfg') as f:
    crusades = get_vc_data(f)
    print(crusades['ecru']['nodes'].keys())
    print(crusades.keys())
    print(str(len(crusades)), 'void crusades loaded')
    print(str(sum([len(v['nodes']) for k,v in crusades.items()])), 'missions loaded')

