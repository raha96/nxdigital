from nxdigital.circuit import circuit
from nxdigital.search import topological_nets_from_outputs
from nxdigital.utils import _net_type

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
