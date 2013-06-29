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

if len(sys.argv) < 3: 
		print """ 

		Delete the last GOP from a trace file.  Currently the last GOP of H.264
		videos is not handled well by this framework.  For this reason the last
		GOP of the SVC to be sent should be purged.

		Usage: %s <original stream's H264AVCDecoder output> <original trace file>

		Where:
		
		<original stream's H264AVCDecoder output>: the screen output obtained
		from the H264AVCDecoder ran using the sent H.264 file as argument. For
		example:
		$ H264AVCDecoderLibTestStatic foreman.264 foreman_null.yuv > originaldecoderoutput.txt

		<original trace file>: the trace file obtained by using the "-pt" option of the
		BitstreamExtractor executable using as argument the original H.264 file.
		For example:
		$ BitstreamExtractorStatic -pt originaltrace.txt foreman.264
		$ attachframenumber.py originaldecoderoutput.txt originaltrace.txt > originaltrace-frameno.txt

		Example:
		$ %s originaldecoderoutput.txt originaltrace-frameno.txt > originaltrace-frameno-nolastgop.txt

		""" % (sys.argv[0], sys.argv[0])
		sys.exit(1)


GOPSIZE = 16
originaldecoderoutputfilename = sys.argv[1]
originaltraceptfilename = sys.argv[2]

# load lines from the original trace file
originaltracefile = open(originaltraceptfilename)
origtracelist = [] 
for line in originaltracefile:
		try:
				nalu = NALU(line)
				nalu.origframe = 0
				origtracelist.append(nalu)
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


tracelist = [nalu for nalu in origtracelist if nalu.packettype == "SliceData" and not nalu.isControlNALU()]
if len(tracelist) != len(decoderlist):
		print >> sys.stderr, "Length problem: %d vs. %d" % (len(tracelist), len(decoderlist))
		sys.exit(1)

# check that tracefile and decoder output match
zippedlists = zip(tracelist, decoderlist)

for tn, dn in zippedlists:
		if tn.lid != dn.lid or tn.tid != dn.tl or tn.qid != dn.ql:
				print >> sys.stderr, "Problem: %d %d %d vs. %d %d %d at %s (frame %d)" % (tn.lid, tn.tid, tn.qid, dn.lid, dn.tl, dn.ql, tn.startpos, dn.frame)
				sys.exit(2)
		tn.frame = dn.realframe
		tn.origframe = dn.frame
		tn.type = dn.type

# print on standard output the filtered tracefile purged from the last GOP 
#print "Start-Pos.  Length  LId  TId  QId   Packet-Type  Discardable  Truncatable"
#print "==========  ======  ===  ===  ===  ============  ===========  ==========="

for tn in [tn for tn in origtracelist if tn.packettype == "StreamHeader" or tn.packettype == "ParameterSet"]:
		print tn

finallist = []
purging = False
for tn in [tn for tn in origtracelist if tn.packettype == "SliceData"]:
		if not purging and tn.origframe <=0:
				finallist.append(tn)
		else:
				purging = True

for tn in finallist[:-1]:
		print tn

