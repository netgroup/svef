#!/usr/bin/env python

#
#  Copyright 2009 Claudio Pisa (claudio dot pisa at clauz dot net)
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


if(len(sys.argv) < 3):
		print """
		Compute the jitter for each NAL unit and the average jitter.
		
		Usage: %s <sent trace file> <received trace file>

		<sent trace file>: JSVM BitstreamExtractor trace file with a
		further column containing the timestamps corresponding to the sending
		time for each NAL unit. This trace may be obtained from the /streamer/
		module.
								
		<received trace file>: JSVM BitstreamExtractor trace file with a
		further column containing the timestamps corresponding to the receiving
		time for each NAL unit. This trace may be obtained from the /receiver/
		module.

		""" % sys.argv[0]
		sys.exit(1)

senttracefilename = sys.argv[1] 
receivedtracefilename = sys.argv[2]

senttracefile = open(senttracefilename)
sentnalulist = []
sentnaludict = {}
for line in senttracefile:
		nalu = NALU(line)
		if nalu.packettype == "SliceData":
				sentnalulist.append(nalu)
				sentnaludict.update({nalu.id: nalu})
senttracefile.close()

receivedtracefile = open(receivedtracefilename)
receivednalulist = []
for line in receivedtracefile:
		nalu = NALU(line)
		if nalu.packettype == "SliceData":
				nalu.senttimestamp = sentnaludict[nalu.id].timestamp
				receivednalulist.append(nalu)
receivedtracefile.close()

def absD(i ,j):
		return abs((j.timestamp - i.timestamp) - (j.senttimestamp - i.senttimestamp))

i=0
predjitter = 0
jitters = []
while i < len(receivednalulist):
		nalui = receivednalulist[i]
		prednalu = receivednalulist[i-1]
		jitter = predjitter + (absD(nalui, prednalu) - predjitter)/16.0
		predjitter = jitter
		if i>0:
				jitters.append(jitter)
				print "0x%x\t%f" % (nalui.id, jitter)
		i+=1


print "Average jitter: %f milliseconds" % (sum(jitters)/len(jitters),)

