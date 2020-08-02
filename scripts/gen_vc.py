#!/usr/bin/env python3

from copy import deepcopy
import os
import re
import sys

from parse_map import get_map_data, AUG_DEFAULTS
from parse_vc import get_vc_data, flatten_name
from templates import format_file

def recursively_parse_missions(mission_directory):
  # The map directory structure is:
  # . 
  #  \-- Ivory
  #     basicmission_1.cfg
  #     basicmission_2.cfg
  #     ...
  #  \-- Ebony
  #     ...
  maps = {}

  for vc_directory in os.listdir(mission_directory):
    vc_dir = os.path.join(mission_directory, vc_directory)
    print(vc_dir)
  #vc_dir = mission_directory
    vc_name = str.lower(os.path.split(os.path.abspath(vc_dir))[-1])
    maps[vc_name] = {}
    for map_file in os.listdir(vc_dir):
      if map_file.endswith('.cfg'):
        with open(os.path.join(vc_dir, map_file)) as f:
          # strip '.cfg' suffix and flatten
          map_name = flatten_name(os.path.split(os.path.abspath(f.name))[-1][:-4])
          v = get_map_data(f)
          maps[vc_name][map_name] = v
          if 'fragment_x' in v:
            print(map_name, v['fragment_x'], v['fragment_y'])
  return maps   

def associate_missions_with_ids(crusades, missions):
  name2id = {vc_name:{node['internal_name']:node['id'] for node in vc_info['nodes'].values()} for vc_name,vc_info in crusades.items()}
  # fill in each mission's ID
  for vc_name,vc_info in missions.items():
    for mission_name, mission_info in vc_info.items():
      mission_info['id'] = name2id[vc_name][mission_name]
  return missions

def augment_crusade(crusade, missions):
  # Add mission data parsed from the mission's map config file to the mission
  # data parsed from the main void crusade config file.
  for mission_name in crusade['nodes'].keys():
    if mission_name not in missions:
      mission_info = deepcopy(AUG_DEFAULTS)
      print('Using defaults for',mission_name)
    else:
      mission_info = missions[mission_name]
    for key in [
        'map_x', 'map_y', 'map_w', 'map_h',
        'fragment_x', 'fragment_y', 'fragment',
        'req_unlocks', 'opt_unlocks', 'enemies' ]:
      crusade['nodes'][mission_name][key] = mission_info[key]
  return crusade

def main(voidcrusade_cfg, mission_dir, outputfile):
  # Grab VC data
  with open(voidcrusade_cfg) as f:
    crusades = get_vc_data(f)
  print(str(len(crusades)), 'void crusades loaded') 
  print(str(sum([len(v['nodes']) for k,v in crusades.items()])), 'missions loaded')

  # Grab mission data
  missions = recursively_parse_missions(mission_dir)
  print(str(len(missions)),'missions loaded')

  # Mission files don't know their own ID. Fill it in.
  missions = associate_missions_with_ids(crusades, missions)

  # Update mission info in crusade data
  for vc_name in crusades.keys():
    crusades[vc_name] = augment_crusade(crusades[vc_name], missions[vc_name])

  # Write out a javascript data file
  with open(outputfile, 'w') as f:
    f.write(format_file(crusades))
    print(f.name,'written')
  

if __name__=='__main__':
  if len(sys.argv)!=4:
    print('Usage:',sys.argv[0],'Cfg/OpenWorld/voidcrusade.cfg Cfg/Map/TarotCampaign/ outputfile.js')
    sys.exit(-1)
  main(*sys.argv[1:])
