
import haystack
from haystack import model, dump_loader
from haystack.model import LoadableMembers
import sys
import struct
from os import uname

import ctypes, ctypes_malloc
from haystack.config import Config
import logging

logging.basicConfig(level=logging.INFO)

def quotechars( chars ):
	return ''.join( ['.', c][c.isalnum()] for c in chars )

def hexdump(data):
  s='%08x '%0
  numwords = len(data)/2
  for i in range(0, numwords*2 ,2):
    s+="%04x "% struct.unpack('<H' ,data[i:i+2])[0]
    if i%0xf==0xe:
      s+="\r\n%08x "%(i+2)
    elif i%2==1:
      s+=" "
  if len(data) % 2:
    s+="%04x "% struct.unpack('<H' ,data[i:])[0]
  return s


try:
  fdump = sys.argv[1]
except IndexError,e:
  fdump = '/home/jal/Compil/python-haystack/test/test-ctypes3.dump.2'

mappings = dump_loader.load(file(fdump,'rb'))
heap = mappings.getHeap()

start = heap.start
orig_addr = start

allocs = ctypes_malloc.getUserAllocations(mappings, heap)

for addr, size in allocs:
  print 'addr: 0x%08x size: 0x%x'% ( addr, size)
  if size < 48:
    print hexdump(heap.readBytes(addr,size))
  print ' ---------------- '
  



