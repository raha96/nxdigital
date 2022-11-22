from .. import circuit
import re

def load_bench(bench:str) -> circuit.circuit():
    out = circuit.circuit()
    
    def process_ios(line:str) -> bool:
        ismatch = re.findall(r"\b(([Ii][Nn][Pp][Uu][Tt])|([Oo][Uu][Tt][Pp][Uu][Tt]))\w*=\w*(", line)
        print(ismatch)

    with open(bench, "r") as benchin:
        for line in benchin:
            # Discard comments
            line = line[:line.find("#")].strip()
            process_ios(line)
    return out