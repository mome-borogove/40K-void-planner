#!/usr/bin/env python3

FILE_TEMPLATE='''
function CrusadeInfo(nodes, index, x, y) {{
  this.nodes = nodes;
  this.index = index;
  this.x = x;
  this.y = y;
}}

function NodeInfo(id, internal_name, x, y, map_x, map_y, map_w, map_h, difficulty, servo, fragment, fragment_x, fragment_y, loot_quality, loot_quantity, loot_rarity, faction, appearance, objective, deps, objective_locs, skull_locs, enemy_locs) {{
  // id: crusade-unique identifier for this mission
  // internal_name: the original neocore name for the mission, canonicalized
  // x: x-coordinate, in % from left
  // y: y-coordinate, in % from top
  // difficulty: the increase in mission difficulty
  // servo: can this mission spawn a servoskull?
  // faction: enemy type found in the map
  // appearance: Normal, Bonus, Secret, Hidden, or End
  // objective: mission objective type
  // deps: function to compute whether the node is accessible, based on an array
  //       signature: f(A), where array A contains integers describing the
  //                  order of the void plan and -1 indicates "not selected"
  this.id = id;
  this.internal_name = internal_name;
  this.x = x;
  this.y = y;
  this.map_x = map_x;
  this.map_y = map_y;
  this.map_w = map_w;
  this.map_h = map_h;
  this.difficulty = difficulty;
  this.servo = servo;
  this.fragment = fragment;
  this.fragment_x = fragment_x;
  this.fragment_y = fragment_y;
  this.loot_quality = loot_quality;
  this.loot_quantity = loot_quantity;
  this.loot_rarity = loot_rarity;
  this.faction = faction;
  this.appearance = appearance;
  this.objective = objective;
  this.deps = deps;
  this.objective_locs = objective_locs;
  this.skull_locs = skull_locs;
  this.enemy_locs  = enemy_locs ;
}}

{crusades}

var crusade_data = new Map([
  {crusade_map}
]);'''
def format_file(crusades):
  crusade_str = '\n'.join([format_crusade(k,v) for k,v in crusades.items()])
  crusade_map_str = format_crusade_map(crusades)
  return FILE_TEMPLATE.format(crusades=crusade_str, crusade_map=crusade_map_str)

CRUSADE_MAP_TEMPLATE = '["{name}", new CrusadeInfo({name}, {index}, {x}, {y})]'
def format_crusade_map(crusades):
  return ',\n'.join([CRUSADE_MAP_TEMPLATE.format(**v) for v in crusades.values()])

CRUSADE_TEMPLATE = '''
var {name} = [
  {nodes}
];'''
def format_crusade(vc_name, vc):
  sorted_nodes = sorted(vc['nodes'].values(), key=lambda n: n['id'])
  node_str = ''.join([format_node(v) for v in sorted_nodes])
  return CRUSADE_TEMPLATE.format(name=vc_name, nodes=node_str)

NODE_TEMPLATE = '''
  new NodeInfo(
    {id},"{internal_name}",
    {x},{y},{map_x},{map_y},{map_w},{map_h},
    {difficulty},{servo},{fragment_bool},{fragment_x},{fragment_y},
    {loot_quality},{loot_quantity},{loot_rarity},
    "{faction}",
    "{appearance}",
    "{objective}",
    [{dep_str}],
    [{obj_loc_str}],
    [{skull_loc_str}],
    [{enemy_loc_str}]),'''
def format_node(nodeinfo):
  s = NODE_TEMPLATE
  dep_str = ', '.join([str(n) for n in nodeinfo['deps']])
  obj_loc_str = ', '.join(['['+str(x)+','+str(y)+']' for x,y in nodeinfo['objective_locs']])
  skull_loc_str = ', '.join(['['+str(x)+','+str(y)+']' for x,y in nodeinfo['skull_locs']])
  enemy_loc_str = ', '.join(['['+str(x)+','+str(y)+']' for x,y in nodeinfo['enemy_locs']])
  if nodeinfo['fragment']:
    fragment_bool = 'true'
  else:
    fragment_bool = 'false'
  return s.format(**nodeinfo, fragment_bool=fragment_bool, dep_str=dep_str, obj_loc_str=obj_loc_str, skull_loc_str=skull_loc_str, enemy_loc_str=enemy_loc_str)
