#!/usr/bin/env python3

from copy import deepcopy
import re
import sys

from parse_vc import parse_vc
from templates import format_file


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
  s = re.sub(r'titkos', r'hidden', s)
  s = re.sub(r'bonusz', r'bonus', s)
  return s

def translate_nodes(nodes):
  name_map = {}
  for i,name in enumerate(nodes):
    name_map[flatten_name(name)] = i

  # Start should always be zero
  if name_map['start']!=0:
    swap_id = name_map['start']
    swap_with = [k for k,v in name_map.items() if v==0][0]
    name_map['start'] = 0
    name_map[swap_with] = swap_id

  new_nodes = deepcopy(nodes)

  for name,node in new_nodes.items():
    node['name'] = flatten_name(name)
    node['id'] = name_map[flatten_name(name)]
    if 'neighbors' in node:
      node['deps'] = [name_map[flatten_name(n)] for n in node['neighbors']]
    else:
      node['deps'] = []

  return new_nodes

def add_start_node(crusade):
  # Add a false node to represent the starting point
  start_node = {}
  start_node['name'] = 'Start'
  start_node['x'] = crusade['x']
  start_node['y'] = crusade['y']
  start_node['faction'] = 'N/A'
  start_node['objective'] = 'N/A'
  start_node['servo'] = 0
  start_node['difficulty'] = 0
  start_node['appearance'] = 'Start'
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

def main(voidcrusade_cfg, outputfile):
  with open(voidcrusade_cfg) as f:
    crusades = parse_vc(f)
  print(str(len(crusades)), 'void crusades loaded') 
  print(str(sum([len(v['nodes']) for k,v in crusades.items()])), 'missions loaded')

  # Substitute mission indices for names
  for crusade in crusades.values():
    print('------------------------------CRUSADE------------------------------')
    print(crusade['name'])
    crusade['nodes'] = add_start_node(crusade)
    crusade['nodes'] = translate_nodes(crusade['nodes'])
    crusade['nodes'] = bidirectional_edges(crusade['nodes'])

  # Write out a javascript data file
  with open(outputfile, 'w') as f:
    f.write(format_file(crusades))
    print(f.name,'written')
  

if __name__=='__main__':
  if len(sys.argv)!=3:
    print('Usage:',sys.argv[0],'Cfg/OpenWorld/voidcrusade.cfg outputfile.js')
  main(*sys.argv[1:])
