from nxdigital.circuit import circuit
from nxdigital.search import topological_nets_from_outputs
from nxdigital.utils import _net_type
from queue import Queue

def fanout_net (cir:circuit, net_name:str) -> set:
    """" Find all nets in the fanout cone of the given net"""
    q = Queue()
    net = cir.net_list[net_name]
    q.put(net)
    marked = set([net])
    coi = []
    while q.qsize():
        net = q.get()
        coi.append(net.name)
        for mod in cir.graph.adj[net]:
            for child_net in cir.graph.adj[mod]:
                if not(child_net in marked):
                    q.put(child_net)
                    marked.add(child_net)
    return coi

def fanout_all (cir:circuit) -> dict:
    """" Find all nets in the fanout cone of every net"""
    nets = topological_nets_from_outputs(cir)
    coi = {}
    for net in nets:
        coi[net] = set([net])
        if cir.net_list[net].ntype != _net_type.OUT:
            for edge in cir.graph.edges:
                if edge[0].name == net:
                    module = list(cir.graph.adj[edge[1]])
                    assert len(module) == 1
                    coi[net] = set.union(coi[net], coi[module[0].name])
    return coi

def fanout_po (cir:circuit) -> dict:
    """" Find all primary outputs in the fanout cone of every net """
    nets = topological_nets_from_outputs(cir)
    focs = {}
    for net in nets:
        if cir.net_list[net].ntype == _net_type.OUT:
            focs[net] = set([net])
        else:
            focs[net] = set()
            for edge in cir.graph.edges:
                if edge[0].name == net:
                    module = list(cir.graph.adj[edge[1]])
                    assert len(module) == 1
                    focs[net] = set.union(focs[net], focs[module[0].name])
    return focs