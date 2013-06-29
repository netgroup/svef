#!/usr/bin/env python

#
#  Copyright 2009 Claudio Pisa (claudio dot pisa at uniroma2 dot it)
#
#  This file is part of SVEF (SVC Streaming Evaluation Framework).
#
#  SVEF is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SVEF is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SVEF.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
from nalulib import *

if(len(sys.argv) < 2):
		print """
		Compute statistics for the given filtered trace file.
		The layers are discriminated on the "QID" field basis.

		Usage: %s <original trace> <filtered received stream's trace> 
		
		<filtered received stream's trace>: the trace file obtained from the
		NAL unit dependency filtering process. For example:
		$ nalufilter originaltrace.txt receivedtrace.txt > filteredtrace.txt

		""" % (os.path.basename(sys.argv[0]))
		sys.exit(1)

class tracestats():
		def __init__(self):
				self.naludict = dict()
				self.bytesdict = dict()
		def __str__(self):
				ret = ""
				for key in self.naludict.keys():
						ret += "layer %d: %d (%d bytes = %d kbytes)\n" % (key, self.naludict[key], self.bytesdict[key], self.bytesdict[key]/1024)
				return ret
		def __repr__(self):
				return self.__str__()
		def addNalu(self, nalu):
				"Add a NALU to the stats"
				layer = nalu.qid
				if self.naludict.has_key(layer):
						self.naludict[layer] += 1
				else:
						self.naludict[layer] = 1
				if self.bytesdict.has_key(layer):
						self.bytesdict[layer] += nalu.length 
				else:
						self.bytesdict[layer] = nalu.length
		def getTotNalus(self):
				tot = 0
				for key in self.naludict.keys():
						tot += self.naludict[key]
				return tot
		def printRelativeStats(self, ts):
				"Print relative (percentage) stats."
				if self.getTotNalus() > ts.getTotNalus():
						orig = self
						other = ts
				else:
						orig = ts
						other = self
				for key in orig.naludict.keys():
						if other.naludict.has_key(key):
								print "layer %d: %f %%" % (key, 100.0*other.naludict[key]/orig.naludict[key])
						else:
								print "layer %d: 0 %%" % (key,)
				

originaltracefilename = sys.argv[1]
filteredtracefilename = sys.argv[2]

# load lines from the original trace file
originaltracefile = open(originaltracefilename)
originalnalulist = [] 
originalnaluheader = []
originalnaludict = {}
for line in originaltracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData":
						originalnalulist.append(nalu)
						originalnaludict.update({nalu.id: nalu})
				else:
						originalnaluheader.append(nalu)
		except IndexError:
				pass
originaltracefile.close()

# load lines from the filtered trace file
filteredtracefile = open(filteredtracefilename)
filteredparsednalulist = [] 
filterednaluidset = set()
for line in filteredtracefile:
		try:
				nalu = NALU(line)
				nalu.ok = True # to mark lines as deleted or not
				if nalu.packettype == "SliceData":
						filteredparsednalulist.append(nalu)
						assert not nalu.id in filterednaluidset
						filterednaluidset.add(nalu.id)
		except IndexError:
				pass
filteredtracefile.close()

# compute statistics
wdo = tracestats()
wdf = tracestats()

for nalu in originalnalulist:
		wdo.addNalu(nalu)

for nalu in filteredparsednalulist:
		wdf.addNalu(nalu)

print wdo
print wdf

wdo.printRelativeStats(wdf)
