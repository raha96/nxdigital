def default_labeldict():
  return {
      "and2": "{{<a>a|<b>b}| and |<y>y}", 
      "nand2": "{{<A>A|<B>B}| nand |<Y>Y}"
  }

def default_cell2gate():
  return {
    "nand2": "nand"
  }

def default_delays():
  return {
    "nand2": 1.5
  }

def default_cells():
  return "\
module nand2 (Y, A, B);\n\
  input A, B;\n\
  output Y;\n\
  nand gate (Y, A, B);\n\
endmodule\
"

def yosys_labeldict():
  return {
      "$and": "{{<A>A|<B>B}| and |<Y>Y}", 
      "$not": "{<A>A| not |<Y>Y}"
  }

def yosys_cell2gate():
  return {
    "$and": "and", 
    "$not": "not"
  }

def bench_eval():
  return {
    "and": lambda a, b: a & b, 
    "nand": lambda a, b: not(a & b), 
    "xor": lambda a, b: a ^ b, 
    "or": lambda a, b: a | b, 
    "buf": lambda a: a, 
    "not": lambda a: not(a)
  }