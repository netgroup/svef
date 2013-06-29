#!/bin/bash

BYTESPERFRAME=608256
WIDTH=704
HEIGHT=576

usage()
{
		echo "Usage: $0 <test-name> <original trace file> <original H.264> <original YUV> <received trace> <fps> <total number of frames> <play-out buffer size> <output PSNR file>"
		echo ""
		echo "Reminder: bytes per frame, width and height are 'hardcoded' into the script:"
		echo "bytes per frame: $BYTESPERFRAME"
		echo "video width: $WIDTH"
		echo "video height: $HEIGHT"
		echo "playout buffer: $PLAYOUTSIZE milliseconds"
}

executeandcheck()
{
		echo ""
		echo $@ 
		echo ""
		eval $@ || exit 2
}

if [ $# != 9 ]; then
		usage
		exit 1
fi;


TESTNAME=$1
ORIGINALTRACE=$2
ORIGINALH264=$3
ORIGINALYUV=$4
RECTRACE=$5
FPS=$6
TOTFRAMES=$7
PLAYOUTSIZE=$8
PSNROUT=$9

FILTERPROGRAM=nalufilter
BITSTREAMEXTRACTOR=BitStreamExtractorStatic
DECODER=H264AVCDecoderLibTestStatic
CONCEALINGPROGRAM=framefiller
PSNRPROGRAM=PSNRStatic
PSNR2MATLAB=psnrtransformer.sh

TMPDIR="./$TESTNAME"
PREFILTEREDTRACE="${TMPDIR}/prefiltered.txt"
FILTEREDTRACE="${TMPDIR}/filtered.txt"
BITSTREAMOUTPUT="${TMPDIR}/bitout.txt"
FILTEREDH264="${TMPDIR}/filtered.264"
FILTEREDYUV="${TMPDIR}/filtered.yuv"
CONCEALEDYUV="${TMPDIR}/concealed.yuv"
MATLABNAME=`echo $TESTNAME | tr "-" "_"`

executeandcheck "mkdir $TMPDIR"
executeandcheck "$FILTERPROGRAM $ORIGINALTRACE $RECTRACE $PLAYOUTSIZE $FPS > $PREFILTEREDTRACE"
executeandcheck "$FILTERPROGRAM $ORIGINALTRACE $PREFILTEREDTRACE $PLAYOUTSIZE $FPS > $FILTEREDTRACE"
executeandcheck "$BITSTREAMEXTRACTOR $ORIGINALH264 $FILTEREDH264 -et $FILTEREDTRACE > $BITSTREAMOUTPUT"
executeandcheck "$DECODER $FILTEREDH264 $FILTEREDYUV"
executeandcheck "$CONCEALINGPROGRAM $FILTEREDTRACE $BYTESPERFRAME $TOTFRAMES $FILTEREDYUV $CONCEALEDYUV"
executeandcheck "tail -n 4 $BITSTREAMOUTPUT"
executeandcheck "$PSNRPROGRAM $WIDTH $HEIGHT $ORIGINALYUV $CONCEALEDYUV > $PSNROUT"
executeandcheck "$PSNR2MATLAB $PSNROUT > ${MATLABNAME}_matlab.txt"

