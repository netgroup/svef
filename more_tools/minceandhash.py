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

# mince and hash

import sys
import os
import commands
import tempfile

if len(sys.argv) < 3:
		print >> sys.stderr, "Usage: %s <original YUV> <frame size (in bytes)>\n" % sys.argv[0]
		sys.exit(1)

def doit(command):
		"execute a command"
		print >> sys.stderr, command 
		ret, stdoe = commands.getstatusoutput(command)
		print >> sys.stderr, stdoe
		if ret!=0:
				sys.exit(3)
		return stdoe


videofilename = sys.argv[1]
framesize = int(sys.argv[2])

sta = os.stat(videofilename)
videosize = sta.st_size
print >> sys.stderr, "File size: %d bytes. Frame size: %d bytes" % (videosize, framesize)

if videosize % framesize != 0:
		print >> sys.stderr, "Problem: file size is not a multiple of frame size. Quitting..."
		sys.exit(2)

# make and get a temporary directory
tmpdir = tempfile.mkdtemp("","wicloconc",".")

times = videosize / framesize
for i in range(times):
		ofname = "%s/%d.yuv" % (tmpdir, i)
		command1 = "dd if=%s of=%s bs=%d skip=%d count=1" % (videofilename, ofname, framesize, i)
		doit(command1)
		command2 = "md5sum %s" % (ofname)
		onehash = doit(command2)
		print onehash.split()[0],"\t", i
		os.remove(ofname)

os.rmdir(tmpdir)



