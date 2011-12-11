#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Loic Jaquemet loic.jaquemet+python@gmail.com
#

__author__ = "Loic Jaquemet loic.jaquemet+python@gmail.com"

import ctypes
import logging
import sys

from haystack import model
from haystack.model import is_valid_address,is_valid_address_value,pointer2bytes,array2bytes,bytes2array,getaddress
from haystack.model import LoadableMembers,RangeValue,NotNull,CString, IgnoreMember, PerfectMatch

from haystack.config import Config
import struct
import libheap
import math

log=logging.getLogger('ctypes_malloc')


class mallocStruct(LoadableMembers):
  ''' defines classRef '''
  pass


def check_inuse(p):
  "extract p's inuse bit"
  return (malloc_chunk.from_address( ctypes.addressof(p) + \
          (p.size & ~libheap.SIZE_BITS)).size & libheap.PREV_INUSE)


if Config.WORDSIZE == 4:
  UINT = ctypes.c_uint32
elif Config.WORDSIZE == 8:
  UINT = ctypes.c_uint64



class malloc_chunk(mallocStruct):
  '''FAKE python representation of a struct malloc_chunk

struct malloc_chunk {

  INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
  INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */

  struct malloc_chunk* fd;         /* double links -- used only if free. */
  struct malloc_chunk* bk;

  /* Only used for large blocks: pointer to next larger size.  */
  struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
  struct malloc_chunk* bk_nextsize;
};
  '''
  def isValid(self, mappings):

    # get the real data headers. size of fields of based on struct definition
    #  (self.prev_size,  self.size) = struct.unpack_from("<II", mem, 0x0)
    real_size = (self.size & ~libheap.SIZE_BITS)

    log.debug('self.prev_size %d'% self.prev_size )
    log.debug('self.size %d'% self.size )
    log.debug('real_size %d'% real_size )

    ## inuse : to know if inuse, you have to look at next_chunk.size & PREV_SIZE bit
    inuse = check_inuse(self) 
    log.debug('is chunk in use ?: %s'% bool(inuse) )
    
    if math.modf(math.log( real_size, 2))[0] > 0.0:
      # not a good value
      log.debug('real_size is not a 2**')
      return False
    
    return True

  def loadMembers(self, mappings, maxDepth, orig_addr):

    if maxDepth == 0:
      log.debug('Maximum depth reach. Not loading any deeper members.')
      log.debug('Struct partially LOADED. %s not loaded'%(self.__class__.__name__))
      return True
    maxDepth-=1
    log.debug('%s loadMembers'%(self.__class__.__name__))
    if not self.isValid(mappings):
      return False
    
    # update virtual fields
    mmap = is_valid_address_value( orig_addr, mappings)
    self.real_size = (self.size & ~libheap.SIZE_BITS)

  def getNextChunk(self, mappings, orig_addr):
    ## do prev_chunk
    if self.prev_size > 0 :
      prev_addr = orig_addr - self.prev_size
      self.prev_chunk.contents = malloc_chunk.from_buffer_copy(mmap.readStruct(prev_addr, malloc_chunk ))
      model.keepRef( self.prev_chunk.contents, malloc_chunk, prev_addr)
    else :
      log.debug('casting to null') 
      self.prev_chunk = ctypes.POINTER(malloc_chunk)()
      log.debug('NOT DOING PREV_Chunk, prev_size is 0')

    ## do next_chunk
    next_addr = orig_addr + self.real_size
    st = malloc_chunk.from_buffer_copy(mmap.readStruct(next_addr, malloc_chunk ))
    if st is None:
      self.next_chunk.contents = None
    else:
      self.next_chunk.contents = st
      print 'st', st
      print 'next_chunk_contents',self.next_chunk.contents
      model.keepRef( self.next_chunk.contents, malloc_chunk, next_addr)
    
    return True

  def getUserData(self, mappings, orig_addr):
    ## inuse : to know if inuse, you have to look at next_chunk.size & PREV_SIZE bit
    inuse = check_inuse(self) 
    data = None
    addr = orig_addr
    mmap = mappings.getMmapForAddr(addr)
    if not mmap:
      log.error('bad orig_addr')
      return False
    
    real_size = (self.size & ~libheap.SIZE_BITS)
    
    if inuse:
      mem = mmap.readBytes(addr, real_size + Config.WORDSIZE)
      if Config.WORDSIZE == 4:
        off = 0x8
      elif Config.WORDSIZE == 8:
        off = 0x10

      return mem[off:off+real_size]

    elif not inuse:
      if Config.WORDSIZE == 4:
        mem = mmap.readBytes(addr, 0x18)
      elif Config.WORDSIZE == 8:
        mem = mmap.readBytes(addr, 0x30)

      if Config.WORDSIZE == 4:
        (self.fd,         \
        self.bk,          \
        self.fd_nextsize, \
        self.bk_nextsize) = struct.unpack_from("<IIII", mem, 0x8)
      elif Config.WORDSIZE == 8:
        (self.fd,         \
        self.bk,          \
        self.fd_nextsize, \
        self.bk_nextsize) = struct.unpack_from("<QQQQ", mem, 0x10)

    return None


malloc_chunk._fields_ = [
    ( 'prev_size' , UINT ), #  INTERNAL_SIZE_T
    ( 'size' , UINT ), #  INTERNAL_SIZE_T with some flags
    # totally virtual
   ]

# cant use 2** expectedValues, there is a mask on sizes...
malloc_chunk.expectedValues = {    }




'''
    def write(self, inferior=None):
        if self.fd == None and self.bk == None:
            inuse = True
        else:
            inuse = False

        if inferior == None:
            inferior = get_inferior()
            if inferior == -1:
                return None

        if inuse:
            if SIZE_SZ == 4:
                mem = struct.pack("<II", self.prev_size, self.size)
                if self.data != None:
                    mem += struct.pack("<%dI" % len(self.data), *self.data)
            elif SIZE_SZ == 8:
                mem = struct.pack("<QQ", self.prev_size, self.size)
                if self.data != None:
                    mem += struct.pack("<%dQ" % len(self.data), *self.data)
        else:
            if SIZE_SZ == 4:
                mem = struct.pack("<IIIIII", self.prev_size, self.size, \
                        self.fd, self.bk, self.fd_nextsize, self.bk_nextsize)
            elif SIZE_SZ == 8:
                mem = struct.pack("<QQQQQQ", self.prev_size, self.size, \
                        self.fd, self.bk, self.fd_nextsize, self.bk_nextsize)

        inferior.write_memory(self.address, mem)

################################################################################
'''

#malloc_chunk.isValid = malloc_chunk_isValid
#malloc_chunk.loadMembers = malloc_chunk_loadMembers
#malloc_chunk.getUserData = malloc_chunk_getUserData


model.registerModule(sys.modules[__name__])


