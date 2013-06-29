#!/usr/bin/env python

import sys

if len(sys.argv) != 2:
		print "Usage: %s <(matlab-ready) PSNR file> " % sys.argv[0]
		sys.exit(1)

f = open(sys.argv[1])
dblist = [float(line.split()[1]) for line in f]
f.close()

newdblist = dblist[initframe:endframe]

outavg = sum(newdblist)/float(len(newdblist))

print "Average is %.2f" % (outavg)

