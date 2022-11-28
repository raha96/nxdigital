from .. import circuit, utils
import networkx as nx

def dump_verilog_str(cir:circuit.circuit, modulename:str="verilog_dump", portmapbyname:bool=True):
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
        print(f"{src} -> {dst}")
        return cir.graph.adj[n1][n2]["port"]
    
    indent = "    "

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
    
    outstr = ""

    outstr += f"module {modulename} (" + (beautify(inps, indent="    ")) + ", \n" + (beautify(outs, indent="    ")) + ");\n"
    outstr += indent + "input " + beautify(inps) + ";\n"
    outstr += indent + "output " + beautify(outs) + ";\n"
    outstr += indent + "wire " + beautify(nets) + ";\n"
    modules = {}
    # Outputs
    for module in cir.module_list:
        node = cir.module_list[module]
        modules[module] = [node.mtype, module, {}]
        net = list(cir.graph.adj[node].keys())[0]
        src = cir.module_list[module]
        port = cir.graph.adj[src][net]["port"]
        modules[module][2][net] = port
    # Inputs
    for net in cir.net_list:
        node = cir.net_list[net]
        for adjnet in cir.graph.adj[node]:
            port = getport(net, adjnet.name, cir, True)
            modules[adjnet.name][2][net] = port
    for modulename in modules:
        module = modules[modulename]
        ports = []
        for port in module[2]:
            if portmapbyname:
                ports.append(f".{module[2][port]}({port})")
            else:
                ports.append(port.name)
        portmap = ", ".join(ports)
        line = indent + module[0] + " " + module[1] + "(" + portmap + ");\n"
        outstr += line
    outstr += "endmodule\n"
    return outstr

def dump_verilog(cir:circuit.circuit, filename:str, modulename="verilog_dump"):
    fout = open(filename, "w")
    fout.write(dump_verilog_str(cir, modulename))
    fout.close()
