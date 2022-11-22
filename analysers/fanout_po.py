from nxdigital.circuit import circuit

def fanout_po (cir:circuit) -> dict:
    """" Find all primary outputs in the fanout cone of every net """
    from nxdigital.search import topoligical_sort_from_outputs
    from nxdigital.utils import _net_type
    nets = topoligical_sort_from_outputs(cir)
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

    