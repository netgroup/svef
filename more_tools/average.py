#!/usr/bin/env python

import sys

if len(sys.argv) != 2:
		print "Usage: %s <file> " % sys.argv[0]
		sys.exit(1)

f = open(sys.argv[1])
dblist = [float(line.split()[0]) for line in f]
f.close()

outavg = sum(dblist)/float(len(dblist))

print "Average is %.2f" % (outavg)

