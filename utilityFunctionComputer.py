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
import tempfile
import os
import threading
import time
from nalulib import * 

BITSTREAMEXTRACTOR = "BitStreamExtractorStatic"
BITSTREAMEXTRACTOR = "/home/clauz/jsvm/bin/BitStreamExtractorStatic"
DECODER = "H264AVCDecoderLibTestStatic"
PSNR = "PSNRStatic"
LAYERLISTS=[]
# (TID, QID)
#classical (order by qid, then tid)
LAYERLISTS.append([(0,0), (1,0), (2,0), (3,0), (4,0), (0,1), (1,1), (2,1), (3,1), (4,1), (0,2), (1,2), (2,2), (3,2), (4,2)])
#LAYERLISTS.append([(0,1), (1,1), (2,1), (3,1), (4,1), (0,2), (1,2), (2,2), (3,2), (4,2)])
#new 
#LAYERLISTS.append([(0,0), (0,1), (0,2), (1,2), (1,1), (1,0), (2,0), (2,1), (2,2), (3,2), (3,1), (3,0), (4,0), (4,1), (4,2)])
#newer
#LAYERLISTS.append([(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2), (3,0), (3,1), (3,2), (4,0), (4,1), (4,2)])
#madness
#LAYERLISTS.append([(0,0), (1,0), (0,1), (1,1), (0,2), (1,2), (2,0), (2,1), (2,2), (3,0), (3,1), (3,2), (4,0), (4,1), (4,2)])
#madness2
#LAYERLISTS.append([(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2), (3,0), (4,0), (3,1), (4,1), (3,2), (4,2)])
#madness3
#LAYERLISTS.append([(0,0), (1,0), (2,0), (3,0), (4,0), (0,1), (0,2), (1,1), (1,2), (2,1), (2,2), (3,1), (3,2), (4,1), (4,2)])

class LayerException(Exception):
		pass

class LayerInfo:
		layerid = ""
		frame_width = ""
		frame_height = ""
		framerate = ""
		bitrate = ""
		minbitrate = ""
		did = ""
		tid = ""
		qid = ""
		computedbitrate = 0
		psnr = 0
		def __init__(self, bitstreamextractorline):
				info = bitstreamextractorline.split()
				if len(info) < 5:
						raise LayerException
				if info[0] == "Layer":
						raise LayerException
				self.layerid = info[0]
				self.frame_width, self.frame_height = info[1].split("x")
				self.framerate = info[2]
				self.bitrate = info[3]
				if len(info) == 6:
						self.minbitrate = info[4]
						self.did, self.tid, self.qid = info[5].strip(")(").split(",")
				else:
						self.did, self.tid, self.qid = info[4].strip(")(").split(",")
				self.psnr = 0
				self.computedbitrate = 0
		def __str__(self):
				res = ""
				res = "%s %sx%s %s %s (%s,%s,%s)" % (self.layerid, self.frame_width, \
								self.frame_height, self.framerate, self.bitrate, self.did, self.tid, self.qid)
				return res
		def setBitrate(self, bitrate):
				self.computedbitrate = bitrate
		def setPsnr(self, psnr):
				self.psnr = psnr


class UtilitySilos():
		__layerinfodict = None
		__lock = None
		__h264filename = None
		__alllayerlist = None
		__originalyuvfilename = None
		__maxtid = -1
		__maxqid = -1
		__originalyuvstat = None
		def __init__(self, h264filename, alllayerlist, originalyuvfilename, totalframes):
				self.__lock = threading.Lock()
				self.__layerinfodict = {}
				self.__h264filename = h264filename
				self.__originalyuvfilename = originalyuvfilename
				self.__originalyuvstat = os.stat(originalyuvfilename)
				self.__totalframes = totalframes
				self.__alllayerlist = alllayerlist[:]
				self.__maxtid = max([layer[0] for layer in self.__alllayerlist])
				self.__maxqid = max([layer[1] for layer in self.__alllayerlist])

				p = os.popen("%s %s" % (BITSTREAMEXTRACTOR, h264filename))
				#TODO: check exit code
				for line in p:
						try:
								li = LayerInfo(line)
								#debug
								print li
								tid = int(li.tid)
								qid = int(li.qid)
								self.__layerinfodict.update({(tid, qid):li})
						except LayerException:
								pass
				for layer in self.__alllayerlist:
						assert self.__layerinfodict.has_key(layer)
		def addLayerList(self, tid, qid, layerlist):
				self.__lock.acquire()
				tmp = self.__layerinfodict[(tid, qid)]
				tmp.layerlist = layerlist[:]
				self.__lock.release()
		def getMaxFrameRate(self):
				self.__lock.acquire()
				res = max([float(self.__layerinfodict[layer].framerate) for layer in self.__alllayerlist])
				self.__lock.release()
				return res
		def getFrameRate(self, tid, qid):
				self.__lock.acquire()
				res = max([float(self.__layerinfodict[layer].framerate) for layer in self.__layerinfodict[(tid, qid)].layerlist])
				self.__lock.release()
				return res
		def getFrameWidth(self, tid, qid):
				self.__lock.acquire()
				res = max([float(self.__layerinfodict[layer].frame_width) for layer in self.__layerinfodict[(tid, qid)].layerlist])
				self.__lock.release()
				return res
		def getFrameHeight(self, tid, qid):
				self.__lock.acquire()
				res = max([float(self.__layerinfodict[layer].frame_height) for layer in self.__layerinfodict[(tid, qid)].layerlist])
				self.__lock.release()
				return res
		def getTotalFrames(self):
				self.__lock.acquire()
				res = self.__totalframes
				self.__lock.release()
				return res
		def reconstructH264FromNALUList(self, nalulist, newh264filename):
				nalutxt = open(newh264filename + ".txt", 'wb', 0)
				h264 = open(self.__h264filename, 'rb', 0)
				newh264 = open(newh264filename, 'wb', 0)
				for nalu in nalulist:
						nalutxt.write(str(nalu)+"\n")
						h264.seek(nalu.id)
						data = h264.read(nalu.length)
						newh264.write(data)
				newh264.close()
				h264.close()
				nalutxt.close()
		def concealNewYuv(self, nalulist, reconstructedyuvfilename, concealedyuvfilename, numberofframes):
				frameset = set([nalu.frame_number for nalu in nalulist if nalu.frame_number>=0])
				framelist = list(frameset)
				framelist.sort()
				framewidth = self.getFrameWidth(self.__maxtid, self.__maxqid)
				frameheight = self.getFrameHeight(self.__maxtid, self.__maxqid)
				bytesperframe = int(framewidth * frameheight * 1.5)

				if len(frameset) == numberofframes:
						print "%d frames counted. No concealing needed. Hardlinking." % len(frameset)
						command1 = "ln %s %s" % (reconstructedyuvfilename, concealedyuvfilename)
						dothem([command1])
						return

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

				assert len(framesequence) == numberofframes

				# make and get a temporary directory
				tmpdir = tempfile.mkdtemp("","/tmp/wicloconc",".")

				# mince the filtered video
				mince(reconstructedyuvfilename, bytesperframe, tmpdir, framelist)

				# create the concealed video
				command1 = "touch %s" % concealedyuvfilename
				command2 = "rm %s" % concealedyuvfilename
				command3 = "touch %s" % concealedyuvfilename
				dothem([command1, command2, command3])

				for frame in framesequence:
						framefilename = "%s/%d.yuv" % (tmpdir, frame)
						command = "cat %s >> %s" % (framefilename, concealedyuvfilename)
						dothem([command])

				assert numberofframes == len(framelist) + addcounter 

				srconcealed = os.stat(concealedyuvfilename)
				assert srconcealed.st_size == bytesperframe * numberofframes 

				command = "rm -rf %s/" % tmpdir
				dothem([command])
		def addBitrate(self, tid, qid, bitrate):
				self.__lock.acquire()
				self.__layerinfodict[(tid, qid)].setBitrate(bitrate)
				assert self.__layerinfodict[(tid, qid)].computedbitrate != 0
				self.__lock.release()
		def addPSNR(self, tid, qid, psnr):
				self.__lock.acquire()
				self.__layerinfodict[(tid, qid)].setPsnr(psnr)
				assert self.__layerinfodict[(tid, qid)].psnr != 0
				self.__lock.release()
		def assertOK(self, tid, qid):
				self.__lock.acquire()
				assert self.__layerinfodict[(tid, qid)].computedbitrate != 0
				assert self.__layerinfodict[(tid, qid)].psnr != 0
				self.__lock.release()
		def __str__(self):
				self.__lock.acquire()
				res = ""
				res += "Filename: %s\n" % self.__h264filename
				res += "Layer order: %s\n" % self.__alllayerlist 
				res += "\n\n"
				maxtid = self.__maxtid
				maxqid = self.__maxqid
				laydict = {}
				i = 1
				for tid, qid in self.__alllayerlist:
						laydict.update({(tid, qid): i})
						i+=1
				res += "QID ^ \n"
				res += "    | \n"
				for qid in range(maxqid,-1,-1):
						res += " %2d | " % qid
						for tid in range(maxtid+1):
								try:
										res += " %7s " % laydict[(tid, qid)]
								except KeyError:
										res += " "*9
						res += "\n"
				res += "    +-"
				res += "-" * (maxtid+1)*9
				res += "----->\n"
				res += "      "
				for tid in range(maxtid+1):
						res += " %7d " % tid
				res += "  TID\n\n\n"
				for layer in self.__alllayerlist:
						info = self.__layerinfodict[layer]
						res += "Layer: %s ; Bitrate (bits/sec): %f ; PSNR: %f \n" % (layer, info.computedbitrate, info.psnr)
				self.__lock.release()
				return res

		def matstr(self):
				self.__lock.acquire()
				res = ""
				for layer in self.__alllayerlist:
						info = self.__layerinfodict[layer]
						res += "%f     %f \n" % (info.computedbitrate, info.psnr)
				self.__lock.release()
				return res




class UtilityWorker(threading.Thread):
		__id = -1
		__layerlist = None
		__nalulist = None
		__headlist = None
		__infosilos = None
		__logfile = None
		def __init__(self, id, layerlist, nalulist, headlist, infosilos):
				threading.Thread.__init__(self)
				self.__id = id
				self.__nalulist = nalulist[:]
				self.__headlist = headlist[:]
				self.__layerlist = layerlist[:]
				self.__infosilos = infosilos
				self.__logfile = open("/tmp/worker%03d.log" % self.__id, 'w', 0)
		def __del__(self):
				self.__logfile.close()
		def run(self):
				currenttid = self.__layerlist[-1][0]
				currentqid = self.__layerlist[-1][1]
				currentnalus = []
				for layer in self.__layerlist:
						ctid, cqid = layer
						tmpnalus = [nalu for nalu in self.__nalulist if nalu.tid == ctid and nalu.qid == cqid]
						currentnalus.extend(tmpnalus)
				currentnalus.sort()
				# Make a new H.264 file
				newh264filename = "%s/video%03d.264" % (tmpdir, self.__id)
				self.__infosilos.reconstructH264FromNALUList(self.__headlist + currentnalus, newh264filename)

				# Decode H.264 file
				newyuvfilename = "%s/video%03d.yuv" % (tmpdir, self.__id)
				logstring, exitcode = dothem("%s %s %s" % (DECODER, newh264filename, newyuvfilename), \
								exitonerror=False, returnexitcode=True)
				self.__logfile.write(logstring + "\n")
				if exitcode != 0:
						return
				
				# Conceal the new YUV
				total_frames = self.__infosilos.getTotalFrames()
				concealedyuvfilename = "%s/concealedvideo%03d.yuv" % (tmpdir, self.__id)
				self.__infosilos.concealNewYuv(self.__headlist + currentnalus, newyuvfilename, concealedyuvfilename, total_frames)
				
				# Compute some data
				#framerate = silos.getFrameRate(currenttid, currentqid)
				framerate = silos.getMaxFrameRate()
				bytecount = sum([nalu.length for nalu in currentnalus])
				framewidth = silos.getFrameWidth(currenttid, currentqid)
				frameheight = silos.getFrameHeight(currenttid, currentqid)
				#bitrate = bytecount*8*framerate/total_frames
				bitrate = os.stat(newh264filename).st_size * 8 / (totalframes / framerate) 
				self.__infosilos.addBitrate(currenttid, currentqid, bitrate)


				# Compute PSNR
				psnrfilename = "%s/psnr%03d.txt" % (tmpdir, self.__id)
				logstring, exitcode = dothem("%s %d %d %s %s > %s" % \
								(PSNR, framewidth, frameheight, originalyuvfilename, concealedyuvfilename, psnrfilename),\
								exitonerror=False, returnexitcode=True)
				self.__logfile.write(logstring + "\n")
				if exitcode != 0:
						return

				psnrfile = open(psnrfilename, 'r')
				for line in psnrfile:
						splitline = line.split()
						try:
								if len(splitline)>1 and splitline[0] == "total":
										psnr = float(splitline[1].replace(",","."))
						except IndexError:
								pass
				psnrfile.close()
				self.__infosilos.addPSNR(currenttid, currentqid, psnr)
				self.__infosilos.assertOK(currenttid, currentqid)



if __name__ == "__main__":
		if(len(sys.argv) < 7):
				print "Usage: %s <Original YUV> <H.264 file> <f-nstamped trace file> <report file> <total frames> <number of threads>" % sys.argv[0]
				sys.exit(1)
				
		originalyuvfilename = sys.argv[1]
		h264filename = sys.argv[2]
		fnstampedtracefilename = sys.argv[3]
		reportfilename = sys.argv[4]
		totalframes = int(sys.argv[5])
		numberofthreads = int(sys.argv[6])

		reportfile = open(reportfilename, 'w', 0)

		nalulist = []
		headlist = []
		tracefile = open(fnstampedtracefilename)
		for line in tracefile:
				try:
						nalu = NALU(line)
						if nalu.packettype == "SliceData":
								nalulist.append(nalu)
						elif nalu.qid != -1:
								headlist.append(nalu)
				except NALUException, IndexError:
						pass
		tracefile.close()

		for currentlayerlist in LAYERLISTS:
				tmpdir = tempfile.mkdtemp("","/tmp/wicloutility", ".")
				silos = UtilitySilos(h264filename, currentlayerlist, originalyuvfilename, totalframes)

				uwlist = []
				i = 1
				while i<=len(currentlayerlist):
						currentlayers = currentlayerlist[:i]
						currenttid = currentlayers[-1][0]
						currentqid = currentlayers[-1][1]
						silos.addLayerList(currenttid, currentqid, currentlayers)
						uw = UtilityWorker(i, currentlayers, nalulist, headlist, silos)
						uwlist.append(uw)
						i+=1

				for uw in uwlist:
						while threading.activeCount() > numberofthreads:
								time.sleep(1)
						uw.start()

				for uw in uwlist:
						uw.join()

				reportfile.write(str(silos))
				reportfile.write("\n\n\n")

		reportfile.close()
		dothem("cat %s" % reportfilename)

		# for automatic graph plotting
		matreportfilename = reportfilename + ".mat"
		matreportfile = open(matreportfilename, 'w', 0)
		matreportfile.write(silos.matstr())
		matreportfile.close()

