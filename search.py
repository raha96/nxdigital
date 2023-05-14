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
            marked[net] = 1
        else:
            marked[net] = 0

    while q.qsize():
        net = q.get()
        order.append(net.name)
        if (net.ntype != _net_type.IN) and (net.ntype != _net_type.INOUT):
            #print(f"{net.name} {len(pred[net])}")
            module = member(pred[net])
            for inpnet in pred[module]:
                marked[inpnet] += 1
                if marked[inpnet] == len(adj[inpnet]):
                    q.put(inpnet)
    return order


def topological_modules_from_outputs (cir:circuit.circuit) -> list:
    order_nets = topological_nets_from_outputs(cir)
    order = []
    pred = cir.graph.pred
    for net in order_nets:
        for mod in pred[cir.net_list[net]]:
            order.append(mod.name)
    return order

def topological_modules_from_inputs (cir:circuit.circuit) -> list:
    """Create a list of module names sorted topologically from PIs to POs."""
    def driven_gate(netname:str) -> str:
        gates = list(cir.graph.adj[net])
        if len(gates):
            return gates[0].name
        # PO
        return None
    def check_gate_add(gatename:str, marked:dict, q:Queue):
        if gatename in marked:
            marked[gatename] += 1
        else:
            marked[gatename] = 1
        indeg = len(cir.graph.pred[cir.module_list[gatename]])
        assert marked[gatename] <= indeg
        if marked[gatename] == indeg:
            q.put(gatename)
    order = []
    marked = {}
    q = Queue()
    # Initialize from PIs
    for netname in cir.net_list:
        net = cir.net_list[netname]
        if net.ntype == _net_type.IN:
            gatename = driven_gate(netname)
            assert gatename
            check_gate_add(gatename, marked, q)
    while q.qsize():
        gatename = q.get()
        order.append(gatename)
        for net in cir.graph.adj[cir.module_list[gatename]]:
            outgate = driven_gate(net.name)
            if outgate:
                check_gate_add(outgate, marked, q)
    return order

def topological_nets_from_inputs (cir:circuit.circuit) -> list:
    def outname(gatename:str) -> str:
        return list(cir.graph.adj[cir.module_list[gatename]].keys())[0].name
    order = []
    for netname in cir.net_list:
        if cir.net_list[netname].ntype == _net_type.IN:
            order.append(netname)
    modorder = topological_modules_from_inputs(cir)
    for modname in modorder:
        order.append(outname(modname))
    return order
