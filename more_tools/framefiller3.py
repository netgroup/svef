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

if(len(sys.argv) < 6):
		print "Usage: %s <original layer 0 YUV> <original layer 0 distorted YUV> <bytes per frame> <distorted YUV> <concealed YUV (output)>" % sys.argv[0]
		print ""
		print "Example: %s foreman-0.yuv foreman-d-0.yuv 152064 foreman-d.yuv foreman-c.yuv" % sys.argv[0]
		sys.exit(1)

originallayer0yuv = sys.argv[1]
distortedlayer0yuv = sys.argv[2]
bytesperframe = int(sys.argv[3])
distortedyuvfilename = sys.argv[4]
concealedyuvfilename = sys.argv[5]

# make and get a temporary directory
tmpdir = tempfile.mkdtemp("","wicloconc",".")
tmpdirorig = "%s/original0" % tmpdir
os.mkdir(tmpdirorig)
tmpdirfilt = "%s/filtered" % tmpdir
os.mkdir(tmpdirfilt)
tmpdiro = "%s/distorted" % tmpdir
os.mkdir(tmpdiro)

# check that sizes are ok
sroriginal0 = os.stat(originallayer0yuv)
srdistorted0 = os.stat(distortedlayer0yuv)
if sroriginal0.st_size % bytesperframe != 0:
		print >> sys.stderr, "Length problem: file size %d of %s is not a multiple of %d" % (sroriginal0.st_size, originallayer0yuv, bytesperframe)
		sys.exit(1)
if srdistorted0.st_size % bytesperframe != 0:
		print >> sys.stderr, "Length problem: file size %d of %s is not a multiple of %d" % (srdistorted0.st_size, distortedlayer0yuv, bytesperframe)
		sys.exit(1)

srdistorted = os.stat(distortedyuvfilename)
assert srdistorted.st_size == srdistorted0.st_size

# mince and hash the original layer 0 yuv and the distorted layer 0 yuv
numberofframes = sroriginal0.st_size / bytesperframe

# mince and hash the original layer0-only file
mince(originallayer0yuv, bytesperframe, tmpdirorig)

# find the hashes
md5dict = makehashdict(tmdirorig) 


# mince and hash the distorted layer-0 only YUV
numberofframesindistortedvideo = srdistorted.st_size / bytesperframe
distortedlayer0file = open(distortedlayer0yuv, 'rb')
offset = 0
for f in range(numberofframesindistortedvideo):
		ofname = "%s/%d.yuv" % (tmpdirfilt, f)
		print ofname
		offile = open(ofname, 'wb')
		distortedlayer0file.seek(offset)
		data = distortedlayer0file.read(bytesperframe)
		offile.write(data)
		offile.close()
		# check that the frame size matches
		srframe = os.stat(ofname)
		assert srframe.st_size == bytesperframe
		offset += bytesperframe
distortedlayer0file.close()

# find the hashes
command = "md5sum %s/*.yuv" % tmpdirfilt
md5out = dothem([command])
framelist = []
for line in md5out.split('\n'):
		md5, file = line.split()
		try:
				corrframe = md5dict[md5]
		except KeyError:
				raise NALUException("corresponding frame not found")
		framelist.append(corrframe)

#debug
print framelist, len(framelist)


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
		raise NALUException("frame not found: %s" % currentframe)


# create a sequence of frames from the distorted YUV, as will appear in the concealed YUV
framesequence = []
addcounter = 0
for i in range(numberofframes):
		if i in framelist:
				framesequence.append(i)
		else:
				concframe = findsubstituteframe(i)
				framesequence.append(concframe)
				addcounter += 1

print "Sequence: ", framesequence
assert len(framesequence) == numberofframes

# load frames from the distorted YUV
distortedyuvfile = open(distortedyuvfilename, 'rb')
distortedyuvdict = {}
offset = 0
for f in range(numberofframesindistortedvideo):
		ofname = "%s/%d.yuv" % (tmpdiro, f)
		print ofname
		offile = open(ofname, 'wb')
		distortedyuvfile.seek(offset)
		data = distortedyuvfile.read(bytesperframe)
		offile.write(data)
		offile.close()
		# check that the frame size matches
		srframe = os.stat(ofname)
		assert srframe.st_size == bytesperframe
		offset += bytesperframe
distortedyuvfile.close()

# create the concealed video
command1 = "rm %s" % concealedyuvfilename
command2 = "touch %s" % concealedyuvfilename
dothem([command1, command2])
for frame in framesequence:
		framefilename = "%s/%d.yuv" % (tmpdiro, frame)
		command = "cat %s >> %s" % (framefilename, concealedyuvfilename)
		dothem([command])

print """Statistics:
		%d frames in original video
		%d frames in distorted video
		%d frames added
		""" % (numberofframes, numberofframesindistortedvideo, addcounter)

assert numberofframes == numberofframesindistortedvideo + addcounter 

srconcealed = os.stat(concealedyuvfilename)
assert srconcealed.st_size == sroriginal0.st_size

