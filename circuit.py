import networkx, pydot
from .utils import _net_type, _node_net, _node_module

class circuit(list):
  def __init__(self):
    self.graph = networkx.DiGraph()
    self.module_list = {}
    self.module_list = {}
    self.name = ""
  
  def __str__(self):
    return f"<nxdigital.circuit;name={self.name}>"
  def __repr__(self):
    return self.__str__()
  
  def set_name(self, name:str):
    self.name = name
  
  def add_net(self, name:str, ntype:_net_type, allowdup:bool=False):
    if (not allowdup) and (name in self.module_list):
      print("Warning: Duplicate net " + name)
    if name in self.module_list:
      print("Warning: " + name + " is both a net name and a module name")
    self.module_list[name] = _node_net(name, ntype)
    self.graph.add_node(self.module_list[name])
  
  def remove_net(self, name:str):
    net = self.module_list[name]
    self.graph.remove_node(net)
    self.module_list.pop(name)
  
  def change_net_type(self, name:str, ntype:_net_type):
    self.module_list[name].ntype = ntype
  
  def rename_net(self, oldname:str, newname:str):
    self.module_list[newname] = self.module_list.pop(oldname)
    self.module_list[newname].name = newname
  
  def add_module(self, name:str, mtype:str, allowdup:bool=False):
    if (not allowdup) and (name in self.module_list):
      print("Warning: Duplicate module " + name)
    if name in self.module_list:
      print("Warning: " + name + " is both a net name and a module name")
    self.module_list[name] = _node_module(name, mtype)
    self.graph.add_node(self.module_list[name])
  
  def remove_module(self, name:str):
    module = self.module_list[name]
    self.graph.remove_node(module)
    self.module_list.pop(name)
  
  def get_ports(self, ntype:_net_type=None) -> list:
    ports = []
    for netname in self.module_list:
      _ntype = self.module_list[netname].ntype
      if (ntype == None and _ntype != _net_type.INT) or (ntype == _ntype):
        ports.append(netname)
    return ports
  
  def map_module(self, name:str, module):
    def inst_name(pref, name):
      return pref + "_" + name
    instance = self.module_list[name]
    if module.name != instance.mtype:
      print(f"Warning: Attempting to map {module.name} as {instance.mtype} instance")
    #ports = module.get_ports()
    portmap = {}
    for net in self.graph.pred[instance]:
      port = self.get_port(net.name, name)
      portmap[port] = net.name
    for net in self.graph.adj[instance]:
      port = self.get_port(name, net.name)
      portmap[port] = net.name
    # Probably leaving some corner cases here with INOUTs...
    # Map names in the module to names in the expanded instance
    namesdict = {}
    # NOTE: This decisively breaks support for modules and nets with the same name
    for netname in module.net_list:
      net = module.net_list[netname]
      if net.ntype == _net_type.INT:
        # Copy all intermediate nets
        newname = inst_name(name, netname)
        self.add_net(newname, net.ntype)
        namesdict[netname] = newname
      else:
        namesdict[netname] = portmap[netname]
    for modulename in module.module_list:
      submodule = module.module_list[modulename]
      newname = inst_name(name, modulename)
      self.add_module(newname, submodule.mtype)
      namesdict[modulename] = newname
    for u, v in module.graph.edges():
      port = module.get_port(u.name, v.name)
      self.add_connection(namesdict[u.name], namesdict[v.name], port=port)
    # Clean up the original submodule and its connections
    killlist = []
    for net in self.graph.pred[instance]:
      killlist.append((net.name, name))
    for net in self.graph.adj[instance]:
      killlist.append((name, net.name))
    for u, v in killlist:
      self.remove_connection(u, v)
    self.remove_module(name)

  def check_for_cycles(self):
    return networkx.simple_cycles(self.graph)
  
  def inputs(self, modulename:str) -> list:
    assert modulename in self.module_list, modulename + " is not a module"
    names = []
    for net in self.graph.pred[self.module_list[modulename]]:
      names.append(net.name)
    return names
  
  def output(self, modulename:str) -> list:
    assert modulename in self.module_list, modulename + " is not a module"
    outs = list(self.graph.succ[self.module_list[modulename]])
    assert len(outs) == 1, "Duplicate nets"
    return outs[0].name
  
  def driver_module(self, netname:str) -> str:
    assert netname in self.module_list, netname + " is not a net"
    parents = list(self.graph.pred[self.module_list[netname]].keys())
    assert len(parents) == 1, netname + " has " + str(len(parents)) + " drivers"
    return parents[0].name
  
  def driven_modules(self, netname:str) -> str:
    assert netname in self.module_list, netname + " is not a net"
    children = list(self.graph.succ[self.module_list[netname]].keys())
    names = []
    for mod in children:
      names.append(mod.name)
    return names
  
  def get_type(self, name:str):
    if name in self.module_list:
      return self.module_list[name].mtype
    if name in self.module_list:
      return self.module_list[name].ntype
    return None
  
  def _retrieve_entity(self, name:str):
    if name in self.module_list:
      return self.module_list[name]
    if name in self.module_list:
      return self.module_list[name]
    assert 0, name + " not found"
  
  def get_port(self, name1:str, name2:str):
    node1 = self._retrieve_entity(name1)
    node2 = self._retrieve_entity(name2)
    return self.graph.get_edge_data(node1, node2)["port"]
  
  def add_connection(self, name1:str, name2:str, port:str):
    if (name1 in self.module_list) and (name2 in self.module_list):
      self.graph.add_edge(self.module_list[name1], self.module_list[name2], port=port)
    elif (name1 in self.module_list) and (name2 in self.module_list):
      self.graph.add_edge(self.module_list[name1], self.module_list[name2], port=port)
    else:
      assert (name1 in self.module_list) or (name1 in self.module_list), f"{name1} not found"
      assert (name2 in self.module_list) or (name2 in self.module_list), f"{name2} not found"
      assert 0, "Net-to-net and module-to-module connections are not allowed."
  
  def remove_connection(self, name1:str, name2:str):
    assert type(name1) == str, f"{name1} is not str, but {type(name1)}"
    assert type(name2) == str, f"{name2} is not str, but {type(name2)}"
    if (name1 in self.module_list) and (name2 in self.module_list):
      self.graph.remove_edge(self.module_list[name1], self.module_list[name2])
    elif (name1 in self.module_list) and (name2 in self.module_list):
      self.graph.remove_edge(self.module_list[name1], self.module_list[name2])
    else:
      assert 0, f"Invalid attempt to remove connection between {name1} and {name2}"
  
  def to_pydot(self, labeldict:dict={}) -> pydot.Dot():
    nx = networkx.DiGraph()
    nx.add_nodes_from(self.graph.nodes)
    
    for n in self.module_list:
      node = self.module_list[n]
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