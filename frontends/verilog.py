from .. import circuit, utils
import networkx as nx

def dump_verilog(cir:circuit.circuit, filename:str, modulename="verilog_dump"):
    def beautify(lst:list, linewidth:int=80, indent:str="    "*2) -> str:
        lines = []
        i = 0
        while i < len(lst):
            cline = lst[i]
            i += 1
            while (i < len(lst) and (len(cline) + 2 + len(lst[i]) <= linewidth)):
                cline += ", " + lst[i]
                i += 1
            lines.append(cline)
            cline = ""
        return (", \n" + indent).join(lines)
    
    def getport(src:str, dst:str, cir:circuit.circuit, dir:bool) -> str:
        # TODO: I'm positive there's a better way to do this via nx functions
        # dir: False -> module to net, True -> net to module
        if dir:
            n1 = cir.net_list[src]
            n2 = cir.module_list[dst]
        else:
            n1 = cir.module_list[src]
            n2 = cir.net_list[dst]
        return cir.graph.adj[n1][n2]["port"]
    
    indent = "    "

    #fout = open(filename, "w")
    inps, outs, nets = [], [], []
    for net in cir.net_list:
        ntype = cir.net_list[net].ntype
        if ntype == utils._net_type.IN:
            inps.append(net)
        elif ntype == utils._net_type.OUT:
            outs.append(net)
        elif ntype == utils._net_type.INT:
            nets.append(net)
        else:
            assert 0
    
    print(f"module {modulename} (" + (beautify(inps, indent="    ")) + ", \n" + (beautify(outs, indent="    ")) + ");" )
    print(indent + "input " + beautify(inps) + ";")
    print(indent + "output " + beautify(outs) + ";")
    print(indent + "wire " + beautify(nets) + ";")
    modules = {}
    # Outputs
    for module in cir.module_list:
        node = cir.module_list[module]
        modules[module] = [node.mtype, module, {}]
        net = list(cir.graph.adj[node].keys())[0].name
        port = getport(module, net, cir, False)
        modules[module][2][net] = port
    # Inputs
    for net in cir.net_list:
        node = cir.net_list[net]
        for adjnet in cir.graph.adj[node]:
            modules[adjnet.name].append(net)
            port = getport(net, module, cir, True)
            print(f"{net} -> {adjnet}: {port}")
    #for module in cir.module_list:
    #    print(modules[module])
    print("endmodule")
    #fout.close()
