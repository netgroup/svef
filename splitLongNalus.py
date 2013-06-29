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
import os
from nalulib import *

if(len(sys.argv) < 3):
		print """
		For each line of a BitstreamExtractor-generated trace file, find
		NALUs that exceed a fixed length and split them in two NALUs.

		Usage: %s <BitsreamExtractor generated trace>  <maximum length>  >  sendingtrace.txt

		Where:

		<BitstreamExtractor generated trace>: the trace file obtained by using
		the "-pt" option of the BitstreamExtractor executable using as argument
		the sent H.264 file, or from the purgeLastGOP.py script. 
		For example:
		$ BitstreamExtractorStatic -pt originaltrace.txt foreman.264

		Example: $ %s originaltrace.txt 65000 > originaltrace-frameno.txt
		""" % (os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0]))
		sys.exit(1)

originaltraceptfilename = sys.argv[1]
maxlen = int(sys.argv[2])

# load lines from the original trace file
originaltracefile = open(originaltraceptfilename)
for line in originaltracefile:
		try:
				nalu = NALU(line)
				if nalu.length == -1:
						pass
				elif nalu.length <= maxlen:
						print nalu
				elif nalu.length > maxlen:
						for n in nalu.meiosis(maxlen):
								print n
		except NALUException:
				pass
originaltracefile.close()


