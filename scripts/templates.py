#!/usr/bin/env python3

FILE_TEMPLATE='''
function CrusadeInfo(nodes, index, x, y) {{
  this.nodes = nodes;
  this.index = index;
  this.x = x;
  this.y = y;
}}

function NodeInfo(id, internal_name, x, y, map_x, map_y, map_w, map_h, difficulty, servo, loot_quality, loot_quantity, loot_rarity, faction, appearance, objective_type, deps, fragments, objectives, skulls, enemies) {{
  this.id = id; // crusade-unique identifier for this mission
  this.internal_name = internal_name; // the neocore name, canonicalized
  this.x = x; // x-coordinate of node map, in % from top left
  this.y = y; // y-coordinate of node map, in % from top left
  this.map_x = map_x; // x-coordinate of minimap, in minimap-units
  this.map_y = map_y; // y-coordinate of minimap, in minimap-units
  this.map_w = map_w; // width of minimap, in minimap-units
  this.map_h = map_h; // height of minimap, in minimap-units
  this.difficulty = difficulty; // increase in VC difficulty mod for this map
  this.loot_quality = loot_quality;
  this.loot_quantity = loot_quantity;
  this.loot_rarity = loot_rarity;
  this.faction = faction; // enemy typ found in this map
  this.appearance = appearance; // Normal, Bonus, Secret, Hidden, or End
  this.objective_type = objective_type; // overall mission objective type
  this.deps = deps; // list of ids of dependencies for this map
  // Marker lists all have the same format: [ ["name", x, y], ... ]
  this.fragments = fragments; // marker list of Info Fragment (singular)
  this.objectives = objectives; // marker list of mission objectives
  this.skulls = skulls; // marker list of possible servoskull spawn points
  this.enemies  = enemies; // marker list of all enemy locations
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

def stringify_marker_list(marker_list):
  return ', '.join(
    [ '["' + str(name) + '",' + str(x) + ',' + str(y) + ']'
      for name,x,y in marker_list ])

NODE_TEMPLATE = '''
  new NodeInfo(
    {id},"{internal_name}",
    {x},{y},{map_x},{map_y},{map_w},{map_h},
    {difficulty},{servo},
    {loot_quality},{loot_quantity},{loot_rarity},
    "{faction}",
    "{appearance}",
    "{objective_type}",
    [{deps_str}],
    [{fragments_str}],
    [{objectives_str}],
    [{skulls_str}],
    [{enemies_str}]),'''
def format_node(nodeinfo):
  s = NODE_TEMPLATE
  deps_str = ', '.join([str(n) for n in nodeinfo['deps']])
  return s.format(**nodeinfo,
                  deps_str=deps_str,
                  fragments_str=stringify_marker_list(nodeinfo['fragments']),
                  objectives_str=stringify_marker_list(nodeinfo['objectives']),
                  skulls_str=stringify_marker_list(nodeinfo['skulls']),
                  enemies_str=stringify_marker_list(nodeinfo['enemies']))
