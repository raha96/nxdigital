from ctypes import util
from .. import circuit, utils
import re

def load_bench(bench:str) -> circuit.circuit:
    out = circuit.circuit()
    moduleindex = 0
    
    def process_ios(line:str, out:circuit.circuit()) -> bool:
        ismatch = re.findall(r"(([Oo][Uu][Tt][Pp][Uu][Tt])|([Ii][Nn][Pp][Uu][Tt]))\s*\(\s*([^\)]+)\s*\)", line)
        if len(ismatch):
            ismatch = ismatch[0]
        if len(ismatch) == 4:
            # I/O detected
            if ismatch[1] != "":
                # output
                if ismatch[3] in out.net_list:
                    print(out.net_list[ismatch[3]].ntype)
                    if out.net_list[ismatch[3]].ntype == utils._net_type.IN:
                        out.net_list[ismatch[3]].ntype = utils._net_type.INOUT
                    else:
                        print("Warning: Duplicate output " + ismatch[3] + " ignored")
                else:
                    out.add_net(ismatch[3], utils._net_type.OUT)
            elif ismatch[2] != "":
                # input
                if ismatch[3] in out.net_list:
                    if out.net_list[ismatch[3]].ntype == utils._net_type.OUT:
                        out.net_list[ismatch[3]].ntype = utils._net_type.INOUT
                    else:
                        print("Warning: Duplicate input " + ismatch[3] + " ignored")
                else:
                    out.add_net(ismatch[3], utils._net_type.IN)
            else:
                assert 0
            return True
        return False
    
    def process_gate(line:str, out:circuit.circuit(), moduleindex:int) -> int:
        ismatch = re.findall(r"(\w+)\s*=\s*(\w+)\s*\(([^)]+)\)", line)
        if len(ismatch):
            ismatch = ismatch[0]
        if len(ismatch) == 3:
            # Gate detected
            _outname = ismatch[0]
            _type = ismatch[1]
            _params = ismatch[2].split(",")
            _nets = [_outname]
            for _net in _params:
                _nets.append(_net.strip())
            for _net in _nets:
                if not _net in out.net_list:
                    out.add_net(_net, utils._net_type.INT)
            modname = "U" + str(moduleindex)
            out.add_module(modname, _type)
            out.add_connection(modname, _outname, "y")
            i = 0
            # TODO: Anything smarter than *this*...
            names = "abcdefghijklmnopqrstuvwxz"
            for _inp in _params:
                out.add_connection(_inp.strip(), modname, names[i])
                i += 1
            return True
        return False

    with open(bench, "r") as benchin:
        for line in benchin:
            # Discard comments
            comment = line.find("#")
            if comment > -1:
                line = line[:comment]
            line = line.strip()
            isio = process_ios(line, out)
            isgate = process_gate(line, out, moduleindex)
            if isgate:
                moduleindex += 1
            #if isio:
            #    print ("IO: " + line)
            #if isgate:
            #    print ("Gate: " + line)
            # A single line can not be I/O AND gate simultanously
            assert not(isio and isgate)
    
    return out


def dump_bench(cir:circuit.circuit) -> str:
    #iotypename = {
    #    utils._net_type.IN: "INPUT", 
    #    utils._net_type.OUT: "OUTPUT"
    #}
    def isio(ntype:utils._net_type) -> bool:
        if ntype == utils._net_type.IN or ntype == utils._net_type.OUT:
            return True
        return False
    
    out = ""
    for net in cir.net_list:
        ntype = cir.net_list[net].ntype
        if isio(ntype):
            if ntype == utils._net_type.IN:
                out += "INPUT(" + net + ")\n"
            elif ntype == utils._net_type.OUT:
                out += "OUTPUT(" + net + ")\n"
            elif ntype == utils._net_type.INOUT:
                out += "INPUT(" + net + ")\n"
                out += "OUTPUT(" + net + ")\n"
    out += "\n"

    for module in cir.module_list:
        modulenode = cir.module_list[module]
        outname = list(cir.graph.adj[modulenode].keys())[0].name
        # TODO: Anything better than alphabetical order
        insdict = {}
        inkeys = []
        ins = []
        for node in cir.graph.pred[modulenode]:
            port = cir.get_port(node.name, module)
            insdict[port] = node.name
            inkeys.append(port)
        inkeys.sort()
        for port in inkeys:
            ins.append(insdict[port])
        if modulenode.commented:
            out += "# "
        out += outname + " = " + modulenode.mtype + "(" + (", ".join(ins)) + ")\n"
        
    return out

def harvest_comments(filename:str) -> str:
    out = ""
    with open(filename, "r") as fin:
        for line in fin:
            sharp = line.find("#")
            if sharp > -1:
                out += line[sharp:] + "\n"
    return out
