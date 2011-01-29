#!/usr/bin/env python
# Decantor: A JSON to CSV converter
# =============================================================================
#
# The MIT License
#
# Copyright (c) 2011, Michael Van Veen, and Gettaround, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json, sys
from itertools import chain, count
from unicodeWriter import UnicodeWriter as csv

class JSONToCSV(object):
  typecheck = lambda self, x: (type(x) == type({})) or (type(x) == type([]))
  def __init__(self, filestr):
    self.json        = json.loads(open(filestr, 'r').read())
    self.symbolTable = self.getSymbolTable()
  
  def grabKeys(self, obj, stack=[], keys={}):
   childKeys = {}
   if (type(obj) == type({})):
     keys   = dict(
                chain(  [(x,                     True) for x in keys.iterkeys()]
                      + [('.'.join(stack + [y]), True)  for y in obj.iterkeys()]
                       ))
     childKeys = [ [ x for x in self.grabKeys( y[1],
                                                stack + [y[0]],
                                                keys).iteritems()
                    ] for y in filter( 
                                lambda x: self.typecheck(x[1]), 
                                obj.iteritems()
                              )]
     childKeys = dict(chain.from_iterable(childKeys))

   elif (type(obj) is type([])):
     childKeys = [ [x for x in self.grabKeys(item, stack, keys).iteritems()]
                     for item in filter(lambda x: self.typecheck(x), obj)  ]
     childKeys = dict(chain.from_iterable(childKeys))

   return(dict(
          chain( childKeys.iteritems(),
                 keys.iteritems()
                )))

  def getSymbolTable(self):
   return(sorted(self.grabKeys(self.json).iterkeys()))

  def readObj(self, obj):
    assert(self.symbolTable)
    keys = dict((x, [obj] + x.split('.')) for x in self.grabKeys(obj))
    if type(obj) == type([]):
      obj = obj.pop()

    assert(type(obj) == type({}))
    # objs returns a dictionary where iterated items (key, value),
    # where key, value are the key as concatenated by self.grabKeys() and its 
    # value from within the object, respectively
    objs = dict(
           [ (key,
              reduce( lambda x, y: \
                      ( (type(x) == type([])) 
                          and len(x) and x.pop().get(y)
                      ) or  ((type(x) == type({})) and x.get(y))
                        or x,
                           stack)
              ) for key, stack in keys.iteritems() 
            ])
    # This is how we build a row
    return [(( objs.has_key(x)
                 and not(self.typecheck(objs[x]))) and unicode(objs[x])
            ) or '' for x in self.symbolTable]
    
  def readRows(self):
    # Only works on lists of json objects
    assert(type(self.json) is type([]))
    return(self.readObj(x) for x in self.json)

  def writeToFile(self, filename):
    with open(filename, 'wb') as outfile:
      csvObj = csv(outfile)
      csvObj.writerow(self.symbolTable)
      csvObj.writerows(self.readRows())

if __name__ == "__main__":
  jsonobj = JSONToCSV(sys.argv[1]).writeToFile(sys.argv[2])
