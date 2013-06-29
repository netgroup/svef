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
import string
from nalulib import *
from bitvector import *
 

if(len(sys.argv) < 3):
		print "Usage: %s <trace file> <H.264 file> " % sys.argv[0]
		sys.exit(1)
		
tracefilename = sys.argv[1]
h264filename = sys.argv[2]
#outh264filename = sys.argv[3]

tracefile = open(tracefilename, 'rb', 0)
h264 = open(h264filename, 'r', 0)
#outh264 = open(outh264filename, 'wb', 0)

print "NAL Position\t TID:\t LID:\t AVC_h(hex)\t SVC1_h(hex)\t SVC2_h(hex)\t SVC3_h(hex)\t"

for line in tracefile:
		try:
			nalu = NALU(line)
			if nalu.id != -1:
				#take the nalu from the 264 file and append it to the outfile
				h264.seek(nalu.id+3)
				dataAVC = h264.read(1)
				databinAVC = BitVector(intVal = (ord(dataAVC[0])))
				databinAVC.pad_from_left(8 - databinAVC.__len__())
				if str(databinAVC) == "00000001" or str(databinAVC) == "00100001" or str(databinAVC) == "01000001" or str(databinAVC) == "01100101":
					print "%x\t %x\t %x\t %s(%s)\n" % (nalu.id, nalu.tid, nalu.lid, str(databinAVC), hex(ord(dataAVC[0])))
				if str(databinAVC) == "00010100" or str(databinAVC) == "00110100" or str(databinAVC) == "01010100" or str(databinAVC) == "01110100":
					h264.seek(nalu.id+4)
					dataSVC1 = h264.read(1)
					databinSVC1 = BitVector(intVal = (ord(dataSVC1[0])))
					databinSVC1.pad_from_left(8 - databinSVC1.__len__())
					h264.seek(nalu.id+5)
					dataSVC2 = h264.read(1)
					databinSVC2 = BitVector(intVal = (ord(dataSVC2[0])))
					databinSVC2.pad_from_left(8 - databinSVC2.__len__())
					h264.seek(nalu.id+6)
					dataSVC3 = h264.read(1)
					databinSVC3 = BitVector(intVal = (ord(dataSVC3[0])))
					databinSVC3.pad_from_left(8 - databinSVC3.__len__())

					print "%x\t %x\t %x\t %s(%s)\t %s(%s)\t %s(%s)\t %s(%s)\n" % (nalu.id, nalu.tid, nalu.lid, str(databinAVC),hex(ord(dataAVC[0])), str(databinSVC1),hex(ord(dataSVC1[0])), str(databinSVC2),hex(ord(dataSVC2[0])), str(databinSVC3),hex(ord(dataSVC3[0]))) 
					#print "%x\t %x\t %x\t %s(%s)\n" % (nalu.id, nalu.tid, nalu.lid, str(databinAVC), hex(ord(dataAVC[0])))


		except NALUException:
				pass
tracefile.close()
h264.close()
#outh264.close()

