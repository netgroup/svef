#!/usr/bin/env python

# take a psnr file and compute the average psnr on a specified range

import sys

if len(sys.argv) < 4:
		print >> sys.stderr, """
		Usage:
		%s <beginning frame> <ending frame> <psnr file1> [<psnr file 2>] 
		""" % (sys.argv[0])
		sys.exit(1)

beginningframe = int(sys.argv[1])
endingframe = int(sys.argv[2])
psnrfilename = sys.argv[5]
try:
		psnrfilename2 = sys.argv[6]
except IndexError:
		psnrfilename2 = None

class PsnrEntry:
		frameno = -1
		value = 0.0

def psnrFile2List(filename):
		psnrs = []
		psnrfile = open(filename)
		try:
				for line in psnrfile:
						words = line.split()
						p = PsnrEntry()
						p.frameno = int(words[0]) 
						p.value = float(words[1].replace(",","."))
						psnrs.append(p)
		except IndexError:
				pass
		psnrfile.close()
		return psnrs

totpsnr = 0.0
psnrs = psnrFile2List(psnrfilename)
pvalues = [p.value for p in psnrs if beginningframe <= p.frameno < endingframe] 
psnr1 = sum(pvalues)/len(pvalues)
print "PSNR 1: %f" % psnr1
totpsnr += psnr1

if psnrfilename2 != None:
		psnrs2 = psnrFile2List(psnrfilename2)
		pvalues = [p.value for p in psnrs2 if beginningframe <= p.frameno < endingframe] 
		psnr2 = sum(pvalues)/len(pvalues)
		print "PSNR 2: %f" % psnr2
		totpsnr += psnr2

print "Total PSNR: %f" % totpsnr

