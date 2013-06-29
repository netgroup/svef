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

# This script takes in input the original trace file and the received trace file (i.e. with
# some lines missing) and attempts to delete the lines from the received trace file that
# depend on lines that have been lost during the transmission.

import sys
import os
from nalulib import *

if(len(sys.argv) < 2):
		print """
		Check the integrity of each level, GOP by GOP

		Usage: %s <received trace file> 
		""" % (os.path.basename(sys.argv[0]),)
		sys.exit(1)

receivedtracefilename = sys.argv[1]

# load lines from the received trace file
receivedtracefile = open(receivedtracefilename)
receivedparsednalulist = [] 
receivednaluidset = set()
for line in receivedtracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData":
						receivedparsednalulist.append(nalu)
						assert not nalu.id in receivednaluidset
						receivednaluidset.add(nalu.id)
		except NALUException, IndexError:
				pass

receivedtracefile.close()
receivedparsednalulist.sort()

# scan the NALUs
stats = []
gopcounter = 0
levelcounter = dict()
for nalu in receivedparsednalulist:
		if nalu.isGOPHead() and nalu.isControlNALU():
				stats.append((gopcounter, levelcounter))
				levelcounter = dict()
				gopcounter += 1
		ppid = 128 * nalu.lid + 8 * nalu.qid + nalu.tid
		if nalu.id in receivednaluidset:
				try:
						levelcounter[ppid] += 1
				except KeyError:
						levelcounter[ppid] = 1


#display collected results
for gopnumber, levelcounter in stats:
		keyz = levelcounter.keys()
		if len(keyz) > 0:
				print "==== GOP: %d ====" % gopnumber
				keyz.sort()
				for k in keyz:
						try:
								num = levelcounter[k]
						except KeyError:
								num = 0
						print "%2d) %2d" % (k, num) 
				



