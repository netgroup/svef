#!/usr/bin/env python

import sys

if len(sys.argv) != 3:
		print "Usage: %s <(matlab-ready) PSNR file> <window size>" % sys.argv[0]
		sys.exit(1)

windowsize = int(sys.argv[2])
f = open(sys.argv[1])
dblist = [float(line.split()[1]) for line in f]
f.close()

zerolist = [0] * (windowsize/2)
newdblist = zerolist + dblist + zerolist
outdblist = []

i=0
j=i+windowsize
while j <= len(newdblist):
		curaverage = sum(newdblist[i:j])/float(windowsize)
		outdblist.append(curaverage)
		i+=1
		j=i+windowsize


for i,element in enumerate(outdblist):
		print "%d\t%f" % (i, element)

