from .. import circuit, utils

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
    print(indent + "wire " + beautify(nets))
    modules = {}
    for module in cir.module_list:
        node = cir.module_list[module]
        modules[module] = [node.name, node.mtype]
        print(modules[module])
    print("endmodule")
    #fout.close()