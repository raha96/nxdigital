from nxdigital.circuit import circuit
from nxdigital.search import topological_nets_from_inputs
from nxdigital.utils import _net_type

def sta_max(cir:circuit, delays:dict) -> dict:
    """Calculate maximum delay for each net between all arcs"""
    nets = topological_nets_from_inputs(cir)
    times = {}
    for n in nets:
        net = cir.module_list[n]
        if net.ntype == _net_type.IN:
            times[n] = 0
        mods = cir.graph.adj[net]
        for mod in mods:
            outs = cir.graph.adj[mod]
            for _out in outs:
                out = _out.name
                if out in times:
                    times[out] = max(times[out], times[n] + delays[mod.mtype])
                else:
                    times[out] = times[n] + delays[mod.mtype]
    return times

def sta_slack(cir:circuit, delays:dict) -> dict:
    """Calculate the available slack for each gate, with the constraint that the total delay is unchanged"""
    slacks = {}
    times = sta_max(cir, delays)
    for n in times:
        net = cir.module_list[n]
        needed = -1
        for mod in cir.graph.adj[net]:
            outnet = cir.graph.adj[mod]
            assert len(outnet) == 1
            for out in outnet:
                slack = times[out.name] - delays[mod.mtype]
            if needed < 0:
                needed = slack
            else:
                needed = min(slack, needed)
        if needed < 0:
            slacks[n] = 0.0
        else:
            slacks[n] = needed - times[n]
    return slacks
