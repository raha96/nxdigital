from nxdigital.circuit import circuit
from nxdigital.search import topological_nets_from_outputs
from nxdigital.utils import _net_type

def fanout_net (cir:circuit, net_name:str) -> set:
    """" Find all nets in the fanout cone of the given net"""
    coi = set([net_name])
    for child_module in cir.graph.adj[cir.net_list[net_name]]:
        child_nets = list(cir.graph.adj[child_module])
        assert len(child_nets) == 1
        child_net = child_nets[0]
        coi.union(fanout_net(cir, child_net.name))
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