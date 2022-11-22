from .. import circuit, utils

def dump_verilog(cir:circuit.circuit, filename:str, modulename="verilog_dump"):
    def beautify(lst:list, linewidth:int=40, indent:str="    "*2) -> str:
        lines = []
        cline = lst[0]
        i = 1
        while i < len(lst):
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
    
    print(f"module {modulename} (" + (", ".join(inps)) + ", " + (", ".join(outs)) + ");" )
    print(indent + "input " + beautify(inps) + ";\n")
    print(indent + "output " + beautify(outs) + ";\n")
    print(indent + "wire " + beautify(nets))
    print("endmodule")
    #fout.close()