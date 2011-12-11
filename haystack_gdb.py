
import haystack

from  haystack import model


TYPE_CODE_REF = None
COMMAND_DATA = None
Command_DATA = None
COMPLETE_NONE = None

class Command:
  def __init__(self, a1, a2):
    pass


class Gdb:

  TYPE_CODE_REF = None
  COMMAND_DATA = None
  Command_DATA = None
  COMPLETE_NONE = None
  
  def read_memory(self, addr, size):
    mmap = model.is_valid_address_value(addr, self.mappings)
    if not mmap :
      raise RuntimeError
    return mmap.readBytes(addr, size)

  class Frame:
    #selected_frame().read_var('main_arena')
    def read_var(self, label):
      raise ValueError

  def __init__(self, mappings, heap):
    self.mappings = mappings
    self.heap = heap
    self.heapReader = self
    self.pid = 42
    
  def parse_and_eval(self,txt):
    '''
    "global_max_fast"
    
    
    '''
    return struct
    
  def lookup_type(self, strtyp):
    if strtyp == 'unsigned long':
      return ctypes.c_uint
    elif strtyp == 'unsigned int':
      return ctypes.c_uint
    return ctypes.c_void_p
  
  def inferiors(self):
    t = [self.heapReader]
    t.extend(self.mappings)
    return t
  
  def selected_frame(self):
    return self.Frame()
