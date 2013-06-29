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

import os
import commands
import sys


class NALUException(BaseException):
		pass

class NALU:
		"This class represents a NALU, i.e. a line in a tracefile"
		startpos = ""
		length = -1
		lid = ""
		tid = ""
		qid = ""
		packettype = ""
		discardable = ""
		truncatable = ""
		timestamp = 0
		frame_number = -1
		parents = None	#NALUs on which this NALU depends
		children = None	#NALUs that depend on this NALU
		tracefileline = ""
		def __init__(self, tracefileline):
				"Take a line from a tracefile, parse it and populate this object's fields"
				self.tracefileline = tracefileline
				self.parents = list()
				self.children = list()
				try:
						stuff = tracefileline.split()
						try:
									self.startpos = stuff[0]
						except IndexError:
								raise NALUException
						try:
									self.id = int(stuff[0], 16)
						except ValueError:
									self.id = -1
						try:
									self.length = int(stuff[1])
						except ValueError:
									self.length = -1 
						try:
									self.lid = int(stuff[2])
						except ValueError:
									self.lid = -1 
						try:
									self.tid = int(stuff[3])
						except ValueError:
									self.tid = -1 
						try:
									self.qid = int(stuff[4])
						except ValueError:
									self.qid = -1 
						self.packettype = stuff[5]
						self.discardable = stuff[6]
						self.truncatable = stuff[7]
						try:
									self.frame_number = int(stuff[8])
						except IndexError:
									self.frame_number = -1
						try:
									self.timestamp = int(stuff[9])
						except IndexError:
									self.timestamp = 0 
				except:
						raise
						raise NALUException

		def __str__(self):
				"The string representation of this object"
				return "%s%8s%5s%5s%5s%14s%12s%12s%8s%13s" % \
							(self.startpos, self.length, self.lid, \
							self.tid, self.qid, self.packettype, self.discardable, \
							self.truncatable, self.frame_number, self.timestamp)

		def __repr__(self):
				return str(self)
		
		def __cmp__(self, other):
				if self.id < other.id:
						return -1
				if self.id > other.id:
						return 1
				return 0

		def isControlNALU(self):
				"This object is a control NALU (i.e. type 6 or 14)?"
				return self.length <= 20 and self.length > 0

		def isGOPHead(self):
				"This object is at the beginning of a GOP?"
				return self.lid == 0 and self.tid == 0 and self.qid == 0

		def getCoarseParentsIds(self):
				"Returns a list of (lid, tid) of the NALUs on which the current object depends"
				if self.lid == 0 and self.tid == 0:
						return []
				elif self.lid == 0:
						return [(self.lid, self.tid - 1)]
				elif self.tid == 0:
						return [(self.lid - 1, self.tid)]
				else:
						return [(self.lid, self.tid - 1), (self.lid - 1, self.tid)]
		
		def getMediumParentsIds(self):
				"Returns a list of (tid, qid) of the NALUs on which the current object depends"
				if self.tid == 0 and self.qid == 0:
						return []
				elif self.qid == 0:
						return [(self.tid-1, 0)]
				else:
						return [(self.tid, self.qid - 1)]
		
		def getAVCParentsIds(self):
				"Returns a list of (tid,) of the NALUs on which the current object depends"
				if self.tid == 0:
						return []
				else:
						return [(self.tid-1,), (self.tid-1)]

		def getMediumId(self):
				"Returns a (tid, qid) tuple"
				return (self.tid, self.qid)

		def getCoarseId(self):
				"Returns a (lid, tid) tuple"
				return (self.lid, self.tid)

		def getAVCId(self):
				"Returns a (tid,) tuple"
				return (self.tid,)
		
		def alldata(self):
				"String representation with the frame number"
				return self.__str__() 

		def copy(self):
				return NALU(self.tracefileline)

		def meiosis(self, maxlen):
				"return a list of NALUs, each with length less than maxlen, resulting from the division of this NALU"
				res = []
				numberofnalus = self.length / maxlen + 1
				avglen = self.length / numberofnalus
				for i in range(numberofnalus):
						n = NALU(self.tracefileline)
						n.length = avglen
						n.id = n.id + avglen * i
						n.startpos = "0x%08x" % n.id
						res.append(n)
				#the remainder
				res[-1].length += self.length % numberofnalus
				return res




class DecoderNALU:
		frame = -1
		lid = -1
		tl = -1
		ql = -1
		type = ""
		bid = -1
		ap = -1
		qp = -1
		original = ""
		def __init__(self, decoderline):
				#    0      1 2  3  4  5  6  7  8   9     10  11 12 13 14 15
				#  Frame    8 ( LId 1, TL 1, QL 0, SVC-P, BId 0, AP 1, QP 30 )
				try:
						fields = decoderline.split()
						self.frame = int(fields[1])
						self.lid = int(fields[4].strip(','))
						self.tl = int(fields[6].strip(','))
						self.ql = int(fields[8].strip(','))
						self.type = fields[9].strip(',')
#						self.bid = int(fields[11].strip(','))
#						self.ap = int(fields[13].strip(','))
#						self.qp = int(fields[15].strip(','))
				except:
						raise NALUException
		def __str__(self):
				return "  Frame   %d ( LId %d, TL %d, QL %d, %s, BId %d, AP %d, QP %d ) " % \
								(self.frame, self.lid, self.tl, self.ql, self.type, self.bid, self.ap, self.qp)
		def __repr__(self):
				return str(self) 

		def alldata(self):
				return str(self) + "    %s  %s" % (self.original, self.realframe)


def mince(filename, bytesperframe, tmpdir, filenames=[]):
		"""Splits a YUV file called filename in bytesperframe big frames into directory tmpdir"""
		sr = os.stat(filename)
		assert sr.st_size % bytesperframe == 0
		numberofframes = sr.st_size / bytesperframe
		if filenames == []:
				filenames = range(numberofframes)
		print "%d vs. %d" % (numberofframes, len(filenames))
		if numberofframes < len(filenames):
				filenames=filenames[:numberofframes]
		elif numberofframes > len(filenames):
				numberofframes = len(filenames)
		assert numberofframes == len(filenames)
		thefile = open(filename, 'rb')
		offset = 0
		for f in filenames:
				ofname = "%s/%d.yuv" % (tmpdir, f)
				print ofname
				offile = open(ofname, 'wb')
				thefile.seek(offset)
				data = thefile.read(bytesperframe)
				offile.write(data)
				offile.close()
				# check that the frame size matches
				srframe = os.stat(ofname)
				assert srframe.st_size == bytesperframe
				offset += bytesperframe
		thefile.close()

def dothem(commandlist):
		"execute a list of commands"
		for command in commandlist:
				print command
				ret, stdoe = commands.getstatusoutput(command)
				print stdoe
				if ret != 0:
						sys.exit(3)
				return stdoe

def makehashdict(yuvdir):
		command = "md5sum %s/*.yuv" % yuvdir 
		md5out = dothem([command])
		md5dict = {}
		for line in md5out.split('\n'):
				md5, file = line.split()
				frameno = int(os.path.splitext(os.path.basename(file))[0])
				md5dict.update({md5: frameno})
		return md5dict

