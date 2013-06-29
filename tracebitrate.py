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
import os
from nalulib import *

if(len(sys.argv) < 3):
		print """
		Compute bitrate statistics for the given trace file

		Usage: %s <trace file> <fps>

		""" % (os.path.basename(sys.argv[0]))
		sys.exit(1)

				
class TraceBitrate():
		def __init__(self):
				self.nalulist = list()
		def addNalu(self, nalu):
				"Add a NALU"
				self.nalulist.append(nalu)
		def __str__(self):
				res = ""
				times = [nalu.timestamp for nalu in self.nalulist]
				maxtime = max(times)
				mintime = min(times)
				if (maxtime - mintime) <= 0:
						framelist = [nalu.frame_number for nalu in self.nalulist]
						maxframe = max(framelist)
						minframe = min(framelist)
						print maxframe, minframe
						tmplist = []
						for nalu in self.nalulist:
								nalu.timestamp = 1000 * nalu.frame_number / fps
								tmplist.append(nalu)
						self.nalulist = tmplist
						times = [nalu.timestamp for nalu in self.nalulist]
						maxtime = max(times)
						mintime = min(times)
						assert maxtime > mintime

				totalbytes = sum([nalu.length for nalu in self.nalulist])
				totalrate = (totalbytes*8*1000) / (maxtime - mintime)
				res += "Bitrate every second (bps):\n"
				cursec = mintime / 1000
				while cursec <= maxtime/1000:
						curnalus = [nalu for nalu in self.nalulist if nalu.timestamp/1000 == cursec]
						curbytes = sum([cnalu.length for cnalu in curnalus])
						curbps = curbytes * 8
						res += "%d\t%d\n" % (cursec - mintime/1000, curbps)
						cursec +=1 

				res += "\nTotal bitrate: %d bits/sec \n\n" % totalrate
				return res



tracefilename = sys.argv[1]
fps = int(sys.argv[2])

# load lines from the trace file
tracefile = open(tracefilename)
nalulist = [] 
naluheader = []
naludict = {}
for line in tracefile:
		try:
				nalu = NALU(line)
				if nalu.packettype == "SliceData":
						nalulist.append(nalu)
						naludict.update({nalu.id: nalu})
				else:
						naluheader.append(nalu)
		except IndexError:
				pass
		except NALUException:
				pass
tracefile.close()


# compute statistics
tb = TraceBitrate()

for nalu in nalulist:
		tb.addNalu(nalu)

print tb

