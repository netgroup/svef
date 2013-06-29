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
		Compute statistics for the given trace file, excluding control NALUs.

		Usage: %s <trace file> [<fps>]

		""" % (os.path.basename(sys.argv[0]))
		sys.exit(1)

class GraphMatrix():
		def __init__(self, gmdict = None):
				if gmdict == None:
						self.data = {}
				else:
						self.data = gmdict
		def set(self,i,j,value):
				self.data.update({(i,j): value})
		def get(self,i,j):
				return self.data[(i,j)]
		def getmax(self):
				"return (maxi, maxj), i.e. the biggest indexes"
				ilist = []
				jlist = []
				for i,j in self.data.keys():
						ilist.append(i)
						jlist.append(j)
				return (max(ilist), max(jlist))
						

class SuperGraph():
		def __init__(self, graphmatrix=None, filterfunc=lambda x: x):
				if graphmatrix == None:
						self.graphmatrix = GraphMatrix()
				else:
						self.graphmatrix = graphmatrix
				self.filterfunc=filterfunc
		def __str__(self):
				maxtid,maxqid = self.graphmatrix.getmax()
				ret = ""
				ret += "\n"
				ret += "QID ^ \n"
				ret += "    | \n"
				for qid in range(maxqid,-1,-1):
						ret += " %2d | " % qid
						for tid in range(maxtid,-1,-1):
								try:
										ret += " %7s " % self.filterfunc(self.graphmatrix.get(maxtid-tid,qid)) 
								except KeyError:
										ret += " "*9
						ret += "\n"
				ret += "    +-"
				ret += "-" * (maxtid+1)*9
				ret += "----->\n"
				ret += "      "
				for tid in range(maxtid+1):
						ret += " %7d " % tid
				ret += "  TID\n\n\n"
				return ret
		def __repr__(self):
				return self.__str__()

class TraceStats():
		def __init__(self):
				self.naludict = dict()
				self.bytesdict = dict()
				self.framecounter = 0
				self.gopsizes=[]
				self.ctrlcounter=1
				self.maxnalulen=0
		def __str__(self):
				ret = ""
				gm = GraphMatrix(self.naludict)
				sg = SuperGraph(gm)
				ret += str(sg)
				gm = GraphMatrix(self.bytesdict)
				sg = SuperGraph(gm, filterfunc=lambda x:"%.2f" % (x*8.0/10**6))
				ret += str(sg)

				keyz = self.naludict.keys()[:]
				def laycmp(x, y):
						xi, xj = x
						yi, yj = y
						revx = (xj, xi)
						revy = (yj, yi)
						if revx < revy:
								return -1
						elif revx == revy:
								return 0
						else:
								return 1
				keyz.sort(cmp=laycmp)
				nalutot=0
				bytestot=0
				for key in keyz:
						ret += "layer %s: %d NALUs\t(%d bytes = %d Kbytes = %.2f Mbits)\tavg len: %.2f bytes\n" \
								% (key, self.naludict[key], self.bytesdict[key], \
								self.bytesdict[key]/1024, self.bytesdict[key]*8.0/10**6, \
								1.0*self.bytesdict[key]/self.naludict[key])
						nalutot += self.naludict[key]
						bytestot += self.bytesdict[key]
				ret += "total: %d NALUs    \t(%d bytes = %d Kbytes = %.2f Mbits)\tavg len: %.2f bytes\tmax NALU len: %d bytes\n" \
								% (nalutot, bytestot, bytestot/1024, bytestot*8.0/10**6, \
								1.0*bytestot/nalutot, self.maxnalulen)
				ret += "\n"
				ret += "Total number of control NALUs (i.e. guessed total number of frames): %d\n" % self.framecounter
				ret += "GOP size (guessed from control NALUs): %.2f\n" % self.getGopSize()
				if fps != None:
						ret += "Total bitrate (guessed): %.2f bits per second\n" % (bytestot*8.0*fps/self.framecounter)
				return ret
		def __repr__(self):
				return self.__str__()
		def addNalu(self, nalu):
				"Add a NALU to the stats"
				if nalu.isControlNALU():
						self.framecounter += 1
						if nalu.tid == 0 and nalu.qid == 0:
								self.gopsizes.append(self.ctrlcounter)
								self.ctrlcounter = 1
						else:
								self.ctrlcounter += 1
						return
				layer = (nalu.tid, nalu.qid)
				if self.naludict.has_key(layer):
						self.naludict[layer] += 1
				else:
						self.naludict[layer] = 1
				if self.bytesdict.has_key(layer):
						self.bytesdict[layer] += nalu.length 
				else:
						self.bytesdict[layer] = nalu.length
				self.maxnalulen = max(self.maxnalulen, nalu.length)
		def getGopSize(self):
				"return the most frequent value"
				gs = {}
				for s in self.gopsizes:
						try:
								v=gs[s] + 1
						except KeyError:
								v=1
						gs.update({s:v})
				maxk = None
				maxv = 0
				for k, v in gs.iteritems():
						if v > maxv:
								maxv = v
								maxk = k
				return maxk
				

tracefilename = sys.argv[1]
try:
		fps = int(sys.argv[2])	
except IndexError:
		fps = None

# load lines from the trace file
tracefile = open(tracefilename)
nalulist = [] 
naluheader = []
naludict = {}
for line in tracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData":
						nalulist.append(nalu)
						naludict.update({nalu.id: nalu})
				else:
						naluheader.append(nalu)
		except IndexError:
				pass
		except NALUException:
				pass
tracefile.close()


# compute statistics
ts = TraceStats()

for nalu in nalulist:
		ts.addNalu(nalu)

print ts
