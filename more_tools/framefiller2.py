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
from nalulib import *

if(len(sys.argv) < 7):
		print "Usage: %s  <original stream's H264AVCDecoderLibTestStatic output> <original stream's BitstreamExtractorStatic output> <filtered received stream's trace> <bytes per frame> <distorted YUV> <concealed YUV (output)>" % sys.argv[0]
		print ""
		print "Example: %s originaldecoderoutput.txt originaltracept.txt filteredtrace.txt 152064 foreman-d.yuv foreman-c.yuv" % sys.argv[0]
		sys.exit(1)

GOPSIZE = 16
originaldecoderoutputfilename = sys.argv[1]
originaltraceptfilename = sys.argv[2]
filteredtracefilename = sys.argv[3]
bytesperframe = int(sys.argv[4])
distortedyuvfilename = sys.argv[5]
concealedyuvfilename = sys.argv[6]

def dothem(commandlist):
		"execute a list of commands"
		for command in commandlist:
				print command
				ret, stdoe = commands.getstatusoutput(command)
				print stdoe
				if ret != 0:
						sys.exit(3)
				return stdoe


# make and get a temporary directory
tmpdir = tempfile.mkdtemp("","wicloconc",".")

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
		print "Length problem: %d vs. %d" % (len(tracelist), len(decoderlist))
		sys.exit(1)


# check that tracefile and decoder output match
zippedlists = zip(tracelist, decoderlist)

for tn, dn in zippedlists:
		if tn.lid != dn.lid or tn.tid != dn.tl or tn.qid != dn.ql:
				print "Problem: %d %d %d vs. %d %d %d" % (tn.lid, tn.tid, tn.qid, dn.lid, dn.tl, dn.ql)
				sys.exit(2)
		tn.frame = dn.realframe

#debug
# print on standard error a copy of the originaltracefile with frame numbers
#for nalu in tracelist:
#	print >> sys.stderr, nalu.alldata() 


# collect the frames that are present in the filtered trace file
frameset = set()
filteredfile = open(filteredtracefilename)
for line in filteredfile:
		newnalu = NALU(line)
		try:
				frameset.add(tracedict[newnalu.id].frame)
		except KeyError:
				pass
filteredfile.close()

framelist = list(frameset)
framelist.sort()
print "%d frames in the filtered received trace: " % len(framelist), framelist

# create the frame files from the yuv file
i=0
for frame in framelist:
		ofname = "%s/%d.yuv" % (tmpdir, frame)
		command = "dd if=%s of=%s bs=%d skip=%d count=1" % (distortedyuvfilename, ofname, bytesperframe, i)
		dothem([command])
		i+=1

numberofframes = 1 + max([decodernalu.realframe for decodernalu in decoderlist])

#i = 0
#newframes = 0
#lostframes = []
#while i < numberofframes:
#		if i in frameset:
#				i+=1
#		else:
#				print "Frame lost: %d/%d" % (i, numberofframes)
#				lostframes.append(i)

def findsubstituteframe(currentframe):
		# search backwards
		i = currentframe - 1
		while i >= 0:
				if i in	framelist:
						return i
				i-=1
		# search forward
		i = currentframe + 1
		while i < numberofframes:
				if i in framelist:
						return i
				i+=1
		# not found
		raise NALUException("frame not found")


framesequence = []
for i in range(numberofframes):
		if i in framelist:
				framesequence.append(i)
		else:
				concframe = findsubstituteframe(i)
				framesequence.append(concframe)

print "Sequence: ", framesequence

newvideofilename = "%s/%s" % (tmpdir, concealedyuvfilename)
command = "touch %s" % newvideofilename
dothem([command])

for frame in framesequence:
		framefname = "%s/%d.yuv" % (tmpdir, frame)
		command = "cat %s >> %s" % (framefname, newvideofilename)
		dothem([command])

command = "mv %s %s" % (newvideofilename, concealedyuvfilename)
dothem([command])

sys.exit(0)

# -----------8<---------------------------------

# perform the error concealing by repeating the received frames in the places left by the lost frames 
newvideofilename = "%s/newvideo.yuv" % tmpdir
command = "cp %s %s" % (distortedyuvfilename, newvideofilename)
dothem([command])

numberofframes = 1 + max([decodernalu.realframe for decodernalu in decoderlist])
i = 0
newframes = 0
while i < numberofframes:
		if i in frameset:
				i+=1
		else:
				print "Frame lost: %d/%d" % (i, numberofframes)
				ofname1 = "%s/first_part.yuv" % tmpdir 
				command1 = "dd if=%s of=%s bs=%d count=%d" % (newvideofilename, ofname1, bytesperframe, i)
				ofname2 = "%s/second_part.yuv" % tmpdir 
				command2 = "dd if=%s of=%s bs=%d skip=%d" % (newvideofilename, ofname2, bytesperframe, i-1)
				command3 = "cat %s/first_part.yuv %s/second_part.yuv > %s" % (tmpdir, tmpdir, newvideofilename)
				#debug
				command4 = "ls -l %s" % tmpdir
				dothem([command1, command2, command3, command4])
				i+=1
				offset+=1
				# statistic
				newframes+=1

command = "cp %s %s" % (newvideofilename, concealedyuvfilename)
dothem([command])

print "%d frames added." % newframes


