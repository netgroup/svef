#!/usr/bin/env python

import sys

if len(sys.argv) != 4:
		print "Usage: %s <(matlab-ready) PSNR file> <initial frame (included)> <ending frame (excluded)>" % sys.argv[0]
		sys.exit(1)

initframe = int(sys.argv[2])
endframe = int(sys.argv[3]) 
f = open(sys.argv[1])
dblist = [float(line.split()[1]) for line in f]
f.close()

newdblist = dblist[initframe:endframe]

outavg = sum(newdblist)/float(len(newdblist))

print "Average PSNR from frame %d (included) to frame %d (excluded) is %.2f" % (initframe, endframe, outavg)

