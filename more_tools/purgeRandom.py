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
import random
from nalulib import *

if len(sys.argv) < 3:
	print "Usage: %s <trace file> <loss probability>" % sys.argv[0]
	sys.exit(1)


tracefilename = sys.argv[1]
lossprobability = float(sys.argv[2])
print >> sys.stderr, lossprobability

# load lines from the filtered tracefile
tracefile=open(tracefilename)
tracelist=[]
naluheader = []
for line in tracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData":
						tracelist.append(nalu)
				elif nalu.id != -1 and nalu.packettype!="SliceData":
						naluheader.append(nalu)
		except NALUException:
				pass
tracefile.close()

# damage the list
damagedtracelist = []
for nalu in tracelist:
		frand = random.random()
		print >> sys.stderr, frand
		if nalu.isControlNALU() or frand > lossprobability:
				damagedtracelist.append(nalu)

print >> sys.stderr, "%d out of %d purged" % (len(tracelist) - len(damagedtracelist), len(tracelist))

# print on standard output the damaged tracefile 
print "Start-Pos.  Length  LId  TId  QId   Packet-Type  Discardable  Truncatable"
print "==========  ======  ===  ===  ===  ============  ===========  ==========="
for tn in naluheader:
		print tn
for tn in damagedtracelist:
		print tn
	


