from cmath import isfinite
from . import search
from . import circuit
from . import cells
from . import utils

def eval(cir:circuit.circuit, inputs:dict, evaldict:dict=cells.bench_eval()) -> dict:
    # Initialize inputs with 'U'
    out = {}
    for netname in cir.net_list:
        if cir.net_list[netname].ntype == utils._net_type.IN:
            out[netname] = "U"
    for netname in inputs:
        out[netname] = inputs[netname]
    order = search.topological_modules_from_inputs(cir)
    for modname in order:
        module = cir.module_list[modname]
        outname = list(cir.graph.adj[module].keys())[0].name
        mtype = module.mtype.lower()
        ins = []
        isuninit = False
        for net in cir.graph.pred[module]:
            if out[net.name] == "U":
                isuninit = True
            else:
                ins.append(out[net.name])
        if isuninit:
            out[outname] = "U"
        else:
            func = evaldict[mtype]
            if len(ins) == 1:
                out[outname] = func(ins[0])
            else:
                buf = func(ins[0], ins[1])
                for v in ins[2:]:
                    buf = func(buf, v)
                out[outname] = buf
    return out