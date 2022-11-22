from .. import circuit, utils
import re

def load_bench(bench:str) -> circuit.circuit():
    out = circuit.circuit()
    moduleindex = 0
    
    def process_ios(line:str, out:circuit.circuit()) -> bool:
        ismatch = re.findall(r"(([Oo][Uu][Tt][Pp][Uu][Tt])|([Ii][Nn][Pp][Uu][Tt]))\s*\(\s*([^\)]+)\s*\)", line)
        if len(ismatch) == 4:
            # I/O detected
            if ismatch[1] != "":
                # output
                out.add_net(ismatch[3], utils._net_type.OUT)
            elif ismatch[2] != "":
                # input
                out.add_net(ismatch[3], utils._net_type.IN)
            else:
                assert 0
            return True
        return False
    
    def process_gate(line:str, out:circuit.circuit(), moduleindex:int) -> int:
        ismatch = re.findall(r"", line)
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
            out.add_connection(modname, _outname, "out")
            i = 0
            for _inp in _params:
                out.add_connection(_inp.strip(), modname, f"in{i}")
                i += 1
            return True
        return False

    with open(bench, "r") as benchin:
        for line in benchin:
            print (line)
            # Discard comments
            line = line[:line.find("#")].strip()
            isio = process_ios(line, out)
            isgate = process_gate(line, out, moduleindex)
            if isgate:
                moduleindex += 1
            if isio:
                print ("IO: " + line)
            if isgate:
                print ("Gate: " + line)
            assert not(isio and isgate)
    return out