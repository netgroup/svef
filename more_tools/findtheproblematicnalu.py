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
import commands
import tempfile
from nalulib import *

if(len(sys.argv) < 2):
		print "Usage: %s  <filtered received stream's trace> <problematic decoding output>" % sys.argv[0]
		print ""
		print "Example: %s filteredtrace.txt decoderoutput.txt" % sys.argv[0]
		sys.exit(1)

GOPSIZE = 16
filteredtracefilename = sys.argv[1]
decoderoutputfilename = sys.argv[2]

tracelist = []
filteredtracefile = open(filteredtracefilename, 'r')
for line in filteredtracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData" and not nalu.isControlNALU():
						tracelist.append(nalu)
		except NALUException, IndexError:
				pass
filteredtracefile.close()

decoderlist = []
decoderfile = open(decoderoutputfilename, 'r')
for line in decoderfile:
		try:
				decnalu = DecoderNALU(line)
				decoderlist.append(decnalu)
		except NALUException, IndexError:
				pass
decoderfile.close()

i = 0
j = 0
probability = len(tracelist) * 1.0
while i < len(tracelist) and j < len(decoderlist):
		tracenalu = tracelist[i]
		decnalu = decoderlist[j]
		if tracenalu.lid == decnalu.lid and tracenalu.tid == decnalu.tl and tracenalu.qid == decnalu.ql:
				i+=1
				j+=1
		else:
				i+=1
				probability-=1

print >> sys.stderr, "Problematic NALU: 0x%x [%f %%]" % (tracenalu.id, 100.0*probability/len(tracelist))
print tracenalu.startpos
if tracelist[i-2].isControlNALU():
		print tracelist[i-2].starpos

