from nxdigital.circuit import circuit

def emit_verilog (cir:circuit, cell2gate:dict={}) -> tuple:
    """Generate Verilog description and testbench for Inversion fault simulation"""
    from nxdigital.utils import _net_type, _node_module
    module, testbench = "", ""
    modulename = "faulty_module"
    indentation = " " * 4
    control_prefix = "_invert_"
    orig_prefix = "_orig_"
    tvnum = 10

    ins, outs, wires = [], [], []
    ctrls, origs = {}, {}

    for net in cir.net_list:
        ntype = cir.net_list[net].ntype
        if ntype == _net_type.IN:
            ins.append(net)
        elif ntype == _net_type.OUT:
            outs.append(net)
        elif ntype == _net_type.INT:
            wires.append(net)
            ctrls[net] = control_prefix + net
            origs[net] = orig_prefix + net
        else:
            assert 0
    
    module += "module " + modulename + " (" + (", ".join(ins)) + ", \n"
    module += indentation * 2 + (", ".join(ctrls.values())) + ", \n"
    module += indentation * 2 + (", ".join(outs)) + ");\n"
    module += indentation + "input " + (", ".join(ins)) + ";\n"
    module += indentation + "input " + (", ".join(ctrls.values())) + ";\n"
    module += indentation + "output " + (", ".join(outs)) + ";\n"
    module += indentation + "wire " + (", ".join(wires)) + ";\n"

    portdict = {}
    for m in cir.module_list:
        #mod = cir.module_list[m]
        portdict[m] = {}
    
    for edge in cir.graph.edges:
        port = cir.graph.edges[edge]["port"]
        mod, wire = "", ""
        if type(edge[0]) == _node_module:
            mod = edge[0].name
            wire = edge[1].name
            if wire in origs:
                wire = origs[wire]
        elif type(edge[1]) == _node_module:
            mod = edge[1].name
            wire = edge[0].name
        else:
            assert 0
        portdict[mod][port] = wire
    
    for m in cir.module_list:
        ports = portdict[m]
        name = cir.module_list[m].name
        mtype = cir.module_list[m].mtype
        if mtype in cell2gate:
            mtype = cell2gate[mtype]
        module += indentation + mtype + " " + name + " ("
        portmap = ""
        for p in ports:
            q = ports[p]
            portmap += "." + p + "(" + q + "), "
        module += portmap[:-2] + ");\n"
    
    for w in ctrls:
        orig = origs[w]
        ctrl = ctrls[w]
        module += indentation + f"assign {w} = {ctrl} ? ~{orig} : {orig};\n"

    module += "endmodule"

    tvs = []
    from random import random
    for _ in range(tvnum):
        tv = f"{len(ins)}'b"
        for __ in range(len(ins)):
            tv += "01"[ int(random() >= 0.5) ]
        tvs.append(tv)

    testbench += f"module {modulename}_tb;\n"
    testbench += indentation + "reg " + (", ".join(ins)) + ";\n"
    testbench += indentation + "reg " + (", ".join(ctrls.values())) + ";\n"
    testbench += indentation + "wire " + (", ".join(outs)) + ";\n"

    testbench += indentation + "wire " + ("_gold, ".join(outs)) + "_gold;\n"
    testbench += indentation + "wire " + ("_diff, ".join(outs)) + "_diff;\n"
    testbench += indentation + "wire diff;\n"

    # CUT instantiation
    portmap = ""
    for i in ins:
        portmap += f".{i}({i}), "
    portmap += "\n" + (indentation * 2)
    for o in outs:
        portmap += f".{o}({o}), "
    portmap += "\n" + (indentation * 2)
    for c in ctrls.values():
        portmap += f".{c}({c}), "
    testbench += indentation + f"{modulename} cut ({portmap[:-2]});\n"

    # Golden circuit instantiation
    portmap = ""
    for i in ins:
        portmap += f".{i}({i}), "
    portmap += "\n" + (indentation * 2)
    for o in outs:
        portmap += f".{o}({o}_gold), "
    portmap += "\n" + (indentation * 2)
    for c in ctrls.values():
        portmap += f".{c}(1'b0), "
    testbench += indentation + f"{modulename} golden ({portmap[:-2]});\n"

    # Miter
    orexp = ""
    for out in outs:
        testbench += indentation + f"assign {out}_diff = {out} ^ {out}_gold;\n"
        orexp += f" | {out}_diff"
    testbench += indentation + f"assign diff = {orexp[3:]};\n"

    testbench += indentation + "\n"

    for net in ctrls:
        testbench += indentation + f"integer cnt_{net} = 0;\n"

    testbench += indentation + "task update;\n"
    testbench += indentation * 2 + "begin\n"
    for net in ctrls:
        testbench += indentation * 3 + f"if ({ctrls[net]} == 1'b1)\n"
        testbench += indentation * 4 + f"cnt_{net} = cnt_{net} + diff;\n"
    testbench += indentation * 2 + "end\n"
    testbench += indentation + "endtask\n"

    testbench += indentation + "\n"

    testbench += indentation + "integer i;\n"
    testbench += indentation + "initial begin\n"
    testbench += indentation * 2 + f"for (i=0; i<{len(ctrls)}; i=i+1) begin\n"

    # Assuming small enough number of control bits
    ctrlstr = "{" + (", ".join(ctrls.values())) + "}"
    testbench += indentation * 3 + f"{ctrlstr} = 2**i;\n"
    # Assuming small enough number of input bits
    instr = "{" + (", ".join(ins)) + "}"
    for i in range(tvnum):
        testbench += indentation * 3 + f"{instr} = {tvs[i]}; #1; update;\n"

    testbench += indentation * 2 + "end\n"

    for ctrl in ctrls:
        testbench += indentation * 2 + f'$display("{ctrl}: %.3f", 1.0 * cnt_{ctrl} / {tvnum});\n'

    testbench += indentation + "end\n"

    testbench += "endmodule\n"

    return (module, testbench)