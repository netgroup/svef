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

if len(sys.argv) < 4:
	print "Usage: %s <original stream's H264AVCDecoderLibTestStatic output> <original stream's trace> <filtered trace>" % sys.argv[0]
	sys.exit(1)


GOPSIZE = 16
originaldecoderoutputfilename = sys.argv[1]
originaltraceptfilename = sys.argv[2]
filteredtracefilename = sys.argv[3]

# load lines from the original trace file
originaltracefile = open(originaltraceptfilename)
tracelist = [] 
tracedict = {}
for line in originaltracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData" and not nalu.isControlNALU():
						tracelist.append(nalu)
						tracedict.update({nalu.id: nalu})
		except NALUException:
				pass
originaltracefile.close()

# load lines from the decoder file
originaldecoderoutputfile = open(originaldecoderoutputfilename)
decoderlist = []
offset =  -2 * GOPSIZE + 1
offsetjustchanged = False
positive = False

for line in originaldecoderoutputfile:
		try:
				decnalu = DecoderNALU(line)

				# find the frame for each line/NALU 
				if decnalu.frame == 0 and not offsetjustchanged:
						offset += GOPSIZE
						offsetjustchanged = True
				elif decnalu.frame > 0 and not offsetjustchanged and not positive: # in the last GOP the sign changes
						offset += GOPSIZE
						positive = True
						offsetjustchanged = True # delete?

				if offset < 0:
						decnalu.realframe = abs(decnalu.frame)
				else:
						decnalu.realframe = offset + abs(decnalu.frame) 
				decoderlist.append(decnalu)
		except NALUException:
				offsetjustchanged = False

originaldecoderoutputfile.close()


if len(tracelist) != len(decoderlist):
		print >> sys.stderr, "Length problem: %d vs. %d" % (len(tracelist), len(decoderlist))
		sys.exit(1)


# check that tracefile and decoder output match
zippedlists = zip(tracelist, decoderlist)
newdecoderlist = []

for tn, dn in zippedlists:
		if tn.lid != dn.lid or tn.tid != dn.tl or tn.qid != dn.ql:
				print >> sys.stderr, "Problem: %d %d %d vs. %d %d %d at %s (frame %d)" % (tn.lid, tn.tid, tn.qid, dn.lid, dn.tl, dn.ql, tn.startpos, dn.frame)
				sys.exit(2)
		tn.frame = dn.realframe
		tn.type = dn.type
		tn.oldframe = dn.frame
		dn.original = tn.startpos
		dn.originalid = tn.id

# load lines from the filtered tracefile
filteredtracefile=open(filteredtracefilename)
filteredtracelist=[]
naluheader = []
for line in filteredtracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData" and not nalu.isControlNALU():
						filteredtracelist.append(nalu)
				elif nalu.lid != -1 and nalu.packettype!="SliceData":
						naluheader.append(nalu)
		except NALUException:
				pass
filteredtracefile.close()

# print on standard output the filtered tracefile purged from B frames
print "Start-Pos.  Length  LId  TId  QId   Packet-Type  Discardable  Truncatable"
print "==========  ======  ===  ===  ===  ============  ===========  ==========="
for tn in naluheader:
		print tn
for tn in filteredtracelist:
		otn = tracedict[tn.id] 
		if otn.oldframe <=0:
				print tn
	
# TO BE FINISHED


