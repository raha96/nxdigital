from nxdigital.circuit import circuit

def validate_ports(cir:circuit):
    adj = cir.graph.adj
    pred = cir.graph.pred
    for netname in cir.module_list:
        net = cir.module_list[netname]
        for gate in adj[net]:
            assert cir.get_port(net.name, gate.name) != None, f"Invalid port name for {net.name} -> {gate.name}"
        for gate in pred[net]:
            assert cir.get_port(gate.name, net.name) != None, f"Invalid port name for {gate.name} -> {net.name}"