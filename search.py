from typing import OrderedDict
from . import circuit
from queue import Queue
from nxdigital.utils import _net_type

def topological_nets_from_outputs (cir:circuit.circuit) -> list:
    """Return a list of circuit nets, sorted by reverse topological order"""
    def member(view):
        assert len(view) == 1
        return list(view.keys())[0]
    
    marked = {}
    order = []
    pred = cir.graph.pred
    adj = cir.graph.adj

    # TODO: Refactor into two functions (sort from some nodes + sort from outputs)

    q = Queue()
    for netname in cir.net_list:
        net = cir.net_list[netname]
        if (net.ntype == _net_type.OUT) or (net.ntype == _net_type.INOUT):
            q.put(net)
            marked[net] = True
        else:
            marked[net] = False

    while q.qsize():
        net = q.get()
        order.append(net.name)
        if (net.ntype != _net_type.IN) and (net.ntype != _net_type.INOUT):
            module = member(pred[net])
            for parent in pred[module]:
                ready = True
                for childmod in adj[parent]:
                    childnet = member(adj[childmod])
                    if not marked[childnet]:
                        ready = False
                        break
            if ready:
                q.put(parent)
                marked[parent] = True
    return order


def topological_modules_from_outputs (cir:circuit.circuit) -> list:
    order_nets = topological_nets_from_outputs(cir)
    order = []
    pred = cir.graph.pred
    for net in order_nets:
        for mod in pred[cir.net_list[net]]:
            order.append(mod.name)
    return order
