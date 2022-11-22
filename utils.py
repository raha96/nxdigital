from enum import Enum

class _net_type (Enum):
  INT = 0
  # Internal
  IN = 1
  OUT = 2

class _node_net():
  def __init__(self, name:str, ntype:_net_type):
    self.name = name
    self.ntype = ntype
    self.value = 'U'
    # U Z X 0 1

  def __hash__(self) -> int:
    return self.name.__hash__()
  
  def __str__(self):
    return self.name


class _node_module():
  def __init__(self, name:str, mtype:str):
    self.name = name
    self.mtype = mtype
  
  def __hash__(self) -> int:
    return self.name.__hash__()

  def __str__(self):
    return self.name