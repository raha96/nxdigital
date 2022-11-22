from .. import circuit

def load_bench(bench:str) -> circuit.circuit():
    out = circuit.circuit()
    print(bench)
    return out