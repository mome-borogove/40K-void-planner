#!/usr/bin/env python3

FILE_TEMPLATE='''
function CrusadeInfo(nodes, index, x, y) {{
  this.nodes = nodes;
  this.index = index;
  this.x = x;
  this.y = y;
}}

function NodeInfo(id, internal_name, x, y, difficulty, servo, faction, appearance, objective, deps) {{
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
  this.difficulty = difficulty;
  this.servo = servo;
  this.faction = faction;
  this.objective = objective;
  this.appearance = appearance;
  this.deps = deps;
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
    {x},{y},{difficulty},{servo},
    "{faction}",
    "{appearance}",
    "{objective}",
    [{dep_str}]),'''
def format_node(nodeinfo):
  s = NODE_TEMPLATE
  dep_str = ', '.join([str(n) for n in nodeinfo['deps']])
  return s.format(**nodeinfo, dep_str=dep_str)
