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
from nalulib import * 

if(len(sys.argv) < 4):
		print "Usage: %s <trace file> <H.264 file> <Output H.264 file>" % sys.argv[0]
		sys.exit(1)
		
tracefilename = sys.argv[1]
h264filename = sys.argv[2]
outh264filename = sys.argv[3]

tracefile = open(tracefilename, 'rb', 0)
h264 = open(h264filename, 'rb', 0)
outh264 = open(outh264filename, 'wb', 0)

for line in tracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype != "SliceData":
						#take the nalu from the 264 file and append it to the outfile
						h264.seek(nalu.id)
						data = h264.read(nalu.length)
						outh264.write(data)
		except NALUException:
				pass
tracefile.close()
h264.close()
outh264.close()


