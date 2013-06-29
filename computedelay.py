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
import os


if(len(sys.argv) < 3):
		print """
		Compute the delay (i.e. the difference between sending and receiving
		times) for each NAL unit and the average.
		
		Usage: %s <received trace file> <fps>

		<received trace file>: JSVM BitstreamExtractor trace file with a
		further column containing the frame number for each NAL unit. This
		trace may be obtained from the receiver module.

		<fps>: frames per second

		""" % os.path.basename(sys.argv[0])
		sys.exit(1)

receivedtracefilename = sys.argv[1]
fps = int(sys.argv[2]) * 1.0
oneframetime = 1000.0 / fps

receivedtracefile = open(receivedtracefilename)
receivednalulist = []
for line in receivedtracefile:
		nalu = NALU(line)
		if nalu.packettype == "SliceData":
				receivednalulist.append(nalu)
receivedtracefile.close()
receivednalulist.sort()

t0 = receivednalulist[0].timestamp 

print "%10s%10s%13s%13s%10s%10s%10s%10s" % ("ID","Frame #","Timestamp", "Expected TS", "Delay","Length","TID","QID")
for nalu in receivednalulist:
		expectedarrivaltime = int(t0 + nalu.frame_number * oneframetime)
		nalu.delay = nalu.timestamp - expectedarrivaltime
		print "%#010x%10d%13d%13d%10d%10d%10x%10x" % (nalu.id, nalu.frame_number, nalu.timestamp, expectedarrivaltime, nalu.delay, nalu.length, nalu.tid, nalu.qid)

delays = [nalu.delay for nalu in receivednalulist]
print "Average delay: %f milliseconds" % (1.0 * sum(delays)/len(delays),)

