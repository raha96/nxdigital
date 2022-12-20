import networkx, pydot
from .utils import _net_type, _node_net, _node_module

class circuit(list):
  def __init__(self):
    self.graph = networkx.DiGraph()
    self.net_list = {}
    self.module_list = {}
  
  def __str__(self):
    return "circuit"
  
  def add_net(self, name:str, ntype:_net_type):
    self.net_list[name] = _node_net(name, ntype)
    self.graph.add_node(self.net_list[name])
  
  def remove_net(self, name:str):
    net = self.net_list[name]
    self.graph.remove_node(net)
    self.net_list.pop(name)
  
  def change_net_type(self, name:str, ntype:_net_type):
    self.net_list[name].ntype = ntype
  
  def rename_net(self, oldname:str, newname:str):
    self.net_list[newname] = self.net_list.pop(oldname)
    self.net_list[newname].name = newname
  
  def add_module(self, name:str, mtype:str):
    self.module_list[name] = _node_module(name, mtype)
    self.graph.add_node(self.module_list[name])
  
  def remove_module(self, name:str):
    module = self.module_list[name]
    self.graph.remove_node(module)
    self.module_list.pop(name)
  
  def check_for_cycles(self):
    return networkx.simple_cycles(self.graph)
  
  def inputs(self, modulename:str) -> list:
    assert modulename in self.module_list, modulename + " is not a module"
    names = []
    for net in self.graph.pred[self.module_list[modulename]]:
      names.append(net.name)
    return names
  
  def driver_module(self, netname:str) -> str:
    assert netname in self.net_list, netname + " is not a net"
    parents = list(self.graph.pred[self.net_list[netname]].keys())
    assert len(parents) == 1, netname + " has " + str(len(parents)) + " drivers"
    return parents[0].name
  
  def driven_modules(self, netname:str) -> str:
    assert netname in self.net_list, netname + " is not a net"
    children = list(self.graph.succ[self.net_list[netname]].keys())
    names = []
    for mod in children:
      names.append(mod.name)
    return names
  
  def get_type(self, name:str):
    if name in self.module_list:
      return self.module_list[name].mtype
    if name in self.net_list:
      return self.net_list[name].ntype
    return None
  
  def _retrieve_entitry(self, name:str):
    if name in self.net_list:
      return self.net_list[name]
    if name in self.module_list:
      return self.module_list[name]
    assert 0, name + " not found"
  
  def get_port(self, name1:str, name2:str):
    node1 = self._retrieve_entitry(name1)
    node2 = self._retrieve_entitry(name2)
    return self.graph.get_edge_data(node1, node2)["port"]
  
  def add_connection(self, name1:str, name2:str, port:str):
    if (name1 in self.net_list) and (name2 in self.module_list):
      self.graph.add_edge(self.net_list[name1], self.module_list[name2], port=port)
    elif (name1 in self.module_list) and (name2 in self.net_list):
      self.graph.add_edge(self.module_list[name1], self.net_list[name2], port=port)
    else:
      assert (name1 in self.net_list) or (name1 in self.module_list), f"{name1} not found"
      assert (name2 in self.net_list) or (name2 in self.module_list), f"{name2} not found"
      assert 0, "Net-to-net and module-to-module connections are not allowed."
  
  def remove_connection(self, name1:str, name2:str):
    assert type(name1) == str, f"{name1} is not str, but {type(name1)}"
    assert type(name2) == str, f"{name2} is not str, but {type(name2)}"
    if (name1 in self.net_list) and (name2 in self.module_list):
      self.graph.remove_edge(self.net_list[name1], self.module_list[name2])
    elif (name1 in self.module_list) and (name2 in self.net_list):
      self.graph.remove_edge(self.module_list[name1], self.net_list[name2])
    else:
      assert 0, f"Invalid attempt to remove connection between {name1} and {name2}"
  
  def to_pydot(self, labeldict:dict={}) -> pydot.Dot():
    nx = networkx.DiGraph()
    nx.add_nodes_from(self.graph.nodes)
    
    for n in self.net_list:
      node = self.net_list[n]
      if node.ntype == _net_type.INT:
        nx.add_node(node, shape="point")
      else:
        nx.add_node(node)
    
    for n in self.module_list:
      node = self.module_list[n]
      if node.mtype in labeldict:
        label = labeldict[node.mtype]
        shape = "record"
      else:
        label = '"' + node.mtype + '"'
        shape = "rectangle"
      nx.add_node(node, shape=shape, label=label)

    dot = networkx.nx_pydot.to_pydot(nx)

    for e in self.graph.edges:
      attrs = self.graph.edges[e]
      u = e[0].name
      v = e[1].name
      if "port" in attrs:
        if u in self.module_list:
          u += ":" + attrs["port"]
        else:
          v += ":" + attrs["port"]
      dot.add_edge(pydot.Edge(u, v))
    
    dot.set_graph_defaults(rankdir="LR")

    return dot


  def escape(self, name:str) -> str:
    # $and$TMP.v:5$1:Y
    return name.replace("$", "_").replace(".", "_").replace(":", "_")

  def load_yosys_json(self, module:dict):
    self.graph.clear()
    netdict = {}
    typedict = {}

    for n in module["netnames"]:
      # Assuming all nets are single bit
      bit = module["netnames"][n]["bits"][0]
      hide = module["netnames"][n]["hide_name"]
      name = self.escape(n)
      #self.add_net(name, _net_type.INT)
      if (not bit in netdict) or (hide == 0):
        netdict[bit] = name
        typedict[bit] = _net_type.INT
    
    for p in module["ports"]:
      # Assuming all ports are single bit
      dir = module["ports"][p]["direction"]
      bit = module["ports"][p]["bits"][0]
      if dir == "input":
        typedict[bit] = _net_type.IN
      elif dir == "output":
        typedict[bit] = _net_type.OUT
      else:
        assert 0
    
    for bit in netdict:
      self.add_net(netdict[bit], typedict[bit])
    
    for m in module["cells"]:
      mtype = module["cells"][m]["type"]
      name = self.escape(m)
      self.add_module(name, mtype)
      for port in module["cells"][m]["port_directions"]:
        dir = module["cells"][m]["port_directions"][port]
        bit = module["cells"][m]["connections"][port][0]
        if dir == "input":
          u = netdict[bit]
          v = name
        elif dir == "output":
          u = name
          v = netdict[bit]
        else:
          assert 0
        self.add_connection(u, v, port)

    #print (f"{netdict}")