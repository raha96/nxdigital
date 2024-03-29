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
            n1 = cir.module_list[src]
            n2 = cir.module_list[dst]
        else:
            n1 = cir.module_list[src]
            n2 = cir.module_list[dst]
        return cir.graph.adj[n1][n2]["port"]
    
    indent = "    "

    netassigns = []

    inps, outs, nets = [], [], []
    for net in cir.module_list:
        ntype = cir.module_list[net].ntype
        if ntype == utils._net_type.IN:
            inps.append(net)
        elif ntype == utils._net_type.OUT:
            outs.append(net)
        elif ntype == utils._net_type.INT:
            nets.append(net)
        elif ntype == utils._net_type.INOUT:
            inps.append(net + "_IN")
            nets.append(net)
            outs.append(net + "_OUT")
            netassigns.append(indent + "assign " + net + " = " + net + "_IN;\n")
            netassigns.append(indent + "assign " + net + "_OUT = " + net + ";\n")
        elif ntype == utils._net_type.STATIC0:
            nets.append(net)
            netassigns.append(indent + "assign " + net + " = 0;\n")
        elif ntype == utils._net_type.STATIC1:
            nets.append(net)
            netassigns.append(indent + "assign " + net + " = 1;\n")
        else:
            assert 0
    
    outstr = ""

    outstr += f"module {modulename} (" + (beautify(inps, indent="    ")) + ", \n" + (beautify(outs, indent="    ")) + ");\n"
    outstr += indent + "input " + beautify(inps) + ";\n"
    outstr += indent + "output " + beautify(outs) + ";\n"
    if len(nets):
        outstr += indent + "wire " + beautify(nets) + ";\n"
    modules = {}
    # Outputs
    for module in cir.module_list:
        node = cir.module_list[module]
        modules[module] = [node.mtype, module, {}, node.commented]
        net = list(cir.graph.adj[node].keys())[0]
        src = cir.module_list[module]
        port = cir.graph.adj[src][net]["port"]
        modules[module][2][net] = port
    # Inputs
    for net in cir.module_list:
        node = cir.module_list[net]
        for adjnet in cir.graph.adj[node]:
            port = getport(net, adjnet.name, cir, True)
            modules[adjnet.name][2][net] = port
    for modulename in modules:
        module = modules[modulename]
        commented = module[3]
        ports = []
        for port in module[2]:
            if portmapbyname:
                ports.append(f".{module[2][port]}({port})")
            else:
                ports.append(f"{port}")
        portmap = ", ".join(ports)
        line = indent
        if commented:
            line += "/* "
        line += module[0] + " " + module[1] + "(" + portmap + ");"
        if commented:
            line += " */"
        line += "\n"

        outstr += line
    
    outstr += "\n"
    for line in netassigns:
        outstr += line
    
    outstr += "endmodule\n"
    return outstr

def dump_verilog(cir:circuit.circuit, filename:str, modulename="verilog_dump"):
    fout = open(filename, "w")
    fout.write(dump_verilog_str(cir, modulename, portmapbyname=False))
    fout.close()
