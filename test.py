
import haystack
from haystack import model, dump_loader
from haystack.model import LoadableMembers
import sys
import struct
from os import uname

import ctypes, ctypes_malloc
from haystack.config import Config
import logging

logging.basicConfig(level=logging.DEBUG)

def quotechars( chars ):
	return ''.join( ['.', c][c.isalnum()] for c in chars )

def hexdump( chars, sep=' ', width=20 ):
  b=''
  while chars:
	  line = chars[:width]
	  chars = chars[width:]
	  line = line.ljust( width, '\000' )
	  b+= "%s%s%s\n" % ( sep.join( "%02x" % ord(c) for c in line ),
		   sep, quotechars( line ))
  return b
  
fdump = '/home/jal/Compil/python-haystack/test/test-ctypes3.dump.1'

mappings = dump_loader.load(file(fdump,'rb'))
heap = mappings.getHeap()

start = heap.start
orig_addr = start

malloc_chunk = ctypes_malloc.malloc_chunk

chunk = heap.readStruct(start, malloc_chunk)
ret = chunk.loadMembers(mappings, 10, orig_addr)
if not ret:
  print 'not loaded'
  raise ValueError
#print chunk

data = chunk.getUserData(mappings, orig_addr)

print chunk.toString('')
print 'user data :\n ', hexdump(data)
print ' ---------------- '

next = chunk.next_chunk
orig_addr = ctypes.addressof(next)
ret = next.loadMembers(mappings, 10, orig_addr)
if not ret:
  print 'not loaded'
  raise ValueError

print next
print 'user data :\n ', hexdump(next.getUserData(mappings, orig_addr))
print ' ---------------- '


