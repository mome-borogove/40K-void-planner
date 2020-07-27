#!/usr/bin/env python3

from copy import deepcopy
import re
import sys

from parse_map import recursively_parse_maps
from parse_vc import parse_vc, flatten_name
from templates import format_file


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
  start_node = {}
  start_node['internal_name'] = 'start'
  start_node['id'] = 0
  start_node['x'] = crusade['x']
  start_node['y'] = crusade['y']
  start_node['faction'] = 'N/A'
  start_node['objective'] = 'N/A'
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

def main(voidcrusade_cfg, map_dir, outputfile):
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
  if len(sys.argv)!=4:
    print('Usage:',sys.argv[0],'Cfg/OpenWorld/voidcrusade.cfg Cfg/Map/TarotCampaign/ outputfile.js')
    sys.exit(-1)
  main(*sys.argv[1:])
