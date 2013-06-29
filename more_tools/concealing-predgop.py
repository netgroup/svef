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
		print "Usage: %s <original decoder output> <original trace file> <damaged trace file>" % sys.argv[0]
		sys.exit(1)


GOPSIZE = 16
originaldecoderoutputfilename = sys.argv[1]
originaltraceptfilename = sys.argv[2]
damagedtracefilename = sys.argv[3]

# load lines from the original trace file
originaltracefile = open(originaltraceptfilename)
originaltracelist = [] 
traceheader = []
for line in originaltracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData":
						originaltracelist.append(nalu)
				elif nalu.id >=0:
						traceheader.append(nalu)
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

# check length
tracelist = [nalu for nalu in originaltracelist if not nalu.isControlNALU()]
if len(tracelist) != len(decoderlist):
		print "Length problem: %d vs. %d" % (len(tracelist), len(decoderlist))
		sys.exit(1)


# check that tracefile and decoder output match
zippedlists = zip(tracelist, decoderlist)

for tn, dn in zippedlists:
		if tn.lid != dn.lid or tn.tid != dn.tl or tn.qid != dn.ql:
				print "Problem: %d %d %d vs. %d %d %d" % (tn.lid, tn.tid, tn.qid, dn.lid, dn.tl, dn.ql)
				sys.exit(2)
		tn.frame = dn.frame


# load lines from the damaged trace file
damagednalulist = []
damagednaludict = {}
damagedtracefile = open(damagedtracefilename)
for line in damagedtracefile:
		try:
				newnalu = NALU(line)
				damagednalulist.append(newnalu)
				damagednaludict.update({newnalu.id: newnalu})
		except NALUException:
				pass
damagedtracefile.close()

# now begin the concealing
cartridge = {}
finallist = []
for nalu in originaltracelist:
		try:
				dnalu = damagednaludict[nalu.id]
				wehaveit = True
		except KeyError:
				wehaveit = False

		if wehaveit:
				if not nalu.isControlNALU():
						cartridge.update({(nalu.frame, nalu.lid, nalu.tid, nalu.qid): nalu})
				finallist.append(nalu)
		elif not nalu.isControlNALU():
				try:
						prednalu = cartridge[(nalu.frame, nalu.lid, nalu.tid, nalu.qid)]
						finallist.append(prednalu)
				except KeyError:
						pass


print "Start-Pos.  Length  LId  TId  QId   Packet-Type  Discardable  Truncatable"
print "==========  ======  ===  ===  ===  ============  ===========  ==========="
for nalu in traceheader:
		print nalu
for nalu in finallist:
		print nalu


