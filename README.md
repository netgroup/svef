# SVEF: Scalable Video-streaming Evaluation Framework

SVEF is a mixed online/offline open-source framework devised to evaluate the
performance of H.264 SVC video streaming. It is written in C and Python and
released under the GNU General Public License.

## Requirements

Although, with small changes, SVEF should work on most platforms, it has been
developed and tested on GNU/Linux operating systems with the following
packages:

 * JSVM reference software
 *  Python 2.5 standard distribution
 *  A C compiler (e.g., GCC - The GNU Compiler Collection)
 *  Bash shell

Moreover, to run the scheduler, a Linux kernel with the Intermediate Queueing
Device (IMQ) module enabled is required. In our tests, Linux kernel version
2.6.24 with the IMQ patch was used.

## Usage Example

At server side:
```
server_side $ H264AVCDecoderLibTestStatic Soccer_SVC_growing.264 Soccer_SVC_growing.yuv > originaldecoderoutput.txt

server_side $ BitStreamExtractorStatic -pt originaltrace.txt Soccer_SVC_growing.264

server_side $ f-nstamp originaldecoderoutput.txt originaltrace.txt > originaltrace-frameno.txt

server_side $ streamer originaltrace-frameno.txt 30 192.168.0.123 4455 Soccer_SVC_growing.264 1 > sent.txt
```

At client side:
```
client_side $ receiver 4455 out.264 50200 > receivedtrace.txt

client_side $ nalufilter originaltrace-frameno.txt receivedtrace.txt 5000 30 > filteredtrace.txt

client_side $ BitStreamExtractorStatic Soccer_SVC_growing.264 Soccer_SVC_growing-filtered.264 -et filteredtrace.txt

client_side $ H264AVCDecoderLibTestStatic Soccer_SVC_growing-filtered.264 Soccer_SVC_growing-filtered.yuv

client_side $ framefiller filteredtrace.txt 608256 1489 Soccer_SVC_growing-filtered.yuv Soccer_SVC_growing-concealed.yuv

client_side $ PSNRStatic 704 576 SOCCER_704x576_30_orig_02x5.yuv Soccer_SVC_growing-concealed.yuv
```

## Documentation

### f-nstamp

For each line of a BitstreamExtractor-generated trace file, add a column with
the frame number corresponding to the NALU associated to that line.
```
Usage: f-nstamp <original stream's H264AVCDecoder output> <BitsreamExtractor generated trace> > sendingtrace.txt
```
Where:
 * original stream's H264AVCDecoder output: the screen output obtained from the
 * H264AVCDecoder ran using the sent H.264 file as argument. For example:
```
$ H264AVCDecoderLibTestStatic foreman.264 foreman_null.yuv > originaldecoderoutput.txt
```
BitstreamExtractor generated trace: the trace file obtained by using the "-pt" option of the BitstreamExtractor executable using as argument the sent H.264 file. For example:
```
$ BitstreamExtractorStatic -pt originaltrace.txt foreman.264
```
Example:
```
$ f-nstamp originaldecoderoutput.txt originaltrace.txt > originaltrace-frameno.txt
```

### streamer

Stream an H.264 SVC video using a custom 12 bytes long header over UDP. This
header's format may be schematized as follows:

```

   0               8              16              24              32 
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ 
   |      lid      |      tid      |      qid      |l|ty |d|t|2|res|  
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                             naluid                            |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           total size          |          frame number         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                            payload                            |
   |                           .........                           |
   |                           .........                           |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                
```
Where:
 * lid, tid, qid (one byte each): are the layer id, temporal id and quality id of the current NAL unit.
 * l (one bit): if set then this is the last NAL unit of the video.
 * ty (two bits): the type of the NAL unit (currently only SliceData NAL units are sent).
 * d (one bit): if set then the NAL unit is discardable.
 * t (one bit): if set then the NAL unit is truncatable.
 * 2 (one bit): if set then the packet contains two NAL units. Short Control NAL units are sent in the same packet as the NAL units that follow them.
 * res (two bits): reserved for future use.
 * naluid (4 bytes): the offset of the NAL unit in the original video.
 * total size (2 bytes): the total size of the packet, including header, in bytes.
 * frame number (2 bytes): the frame to which the NAL unit belongs, departing from 0.

```
Usage: streamer <tracefile> <fps> <destination_address> <port> <video file> [<seconds to wait before writing to standard output>]
```
Where:
 * tracefile: a BitstreamExtractor trace with frame numbers attached. This tracefile may be yield by the f-nstamp tool. For example:
```
$ H264AVCDecoderLibTestStatic Soccer_SVC_growing.264 Soccer_SVC_growing.yuv > originaldecoderoutput.txt
$ BitStreamExtractorStatic -pt originaltrace.txt Soccer_SVC_growing.264
$ f-nstamp originaldecoderoutput.txt originaltrace.txt > originaltrace-frameno.txt
```
 * fps: video frames per second.
 * destination_address: destination IPv4 address.
 * port: destination UDP port.
 * video file: H.264 SVC video file.
 * seconds to wait before writing to standard output: this optional argument is
useful if multiple streamings are ran together, as writing to standard output
may consume resources and interfere with other streamings that are in progress.
The default is to wait 45 sedconds after the streaming is finished.

Example:
```
$ streamer originaltrace-frameno.txt 30 192.168.0.123 4455 Soccer_SVC_growing.264 1 > sent.txt
```

### receiver

Receive an H.264 SVC video streaming on an UDP port and write a JSVM
BistreamExtractor compatible tracefile.
```
Usage: receiver <listening port> <output H.264 file> <video duration in milliseconds>
```
Where:
 * listening port: the UDP port on which to listen for an incoming stream.
 * output H.264 file: the file to which to output the incoming video.
 * video duration in milliseconds: stop receiving and quit after this time has elapsed.

Example:
```
$ receiver 4455 out.264 50200 > receivedtrace.txt
```

### nalufilter

Filter the NAL units that have unsatisfied dependencies and emulate a play-out
buffer, dropping NAL units that were received too late. SVC Medium Grain
Scalability version.
```
Usage: nalufilter <sent stream trace file> <received trace file> <play out buffer in milliseconds> <frames per second> > <filtered trace file>
```
Where:
 * sent stream trace file: the trace file obtained from the f-nstamp tool, using 
as the argument the trace obtained with the "-pt" option of the JSVM
BitstreamExtractor tool, using the sent H.264 as the argument. For example:
```
$ BitstreamExtractorStatic -pt originaltrace.txt foreman.264
$ f-nstamp originaldecoderoutput.txt originaltrace.txt > originaltrace-frameno.txt
received trace file: the trace file obtained from the receiver module. For example:
$ ./receiver 4455 out.264 20000 > receivedtrace.txt
```

Example:
```
$ nalufilter originaltrace-frameno.txt receivedtrace.txt 5000 30 > filteredtrace.txt
```

### framefiller

Perform frame filling (a naive form of concealing) on a received YUV video.
```
Usage: framefiller <filtered received stream's trace> <bytes per frame> <total frames> <distorted YUV> <concealed YUV (output)>
```
Where:
 * filtered received stream's trace: the trace file obtained from the NAL unit dependency filtering process. For example:
```
$ nalufilter originaltrace-frameno.txt receivedtrace.txt > filteredtrace.txt
```
 * bytes per frame: length in bytes of each YUV frame, obtained from width*height*1.5. i.e. 152064 for CIF, 608256 for 4CIF, 4866048 for HD.
 * total frames: total number of frames in the original video.
 * distorted YUV: the received YUV, reconstructed from the filtered trace file using the JSVM tools. For example:
```
$ BitStreamExtractorStatic Soccer_SVC_growing.264 Soccer_SVC_growing-filtered.264 -et filteredtrace.txt
$ H264AVCDecoderLibTestStatic Soccer_SVC_growing-filtered.264 Soccer_SVC_growing-filtered.yuv
```
 * concealed YUV (output): the file containing the YUV resulting from the frame filling process. For each missing frame, the previously available frame is inserted.

Example:
```
$ framefiller filteredtrace.txt 608256 1489 Soccer_SVC_growing-filtered.yuv Soccer_SVC_growing-concealed.yuv
```

## Scientific Referral

If you need to refer to this software please use the following:
**A. Detti, G. Bianchi, W. Kellerer, et al. "SVEF: an Open-Source Experimental Evaluation Framework" in Proc. of IEEE MediaWIN 2009, Sousse, Tunisia**
or, equivalently, the following BibTeX entry:
```
@INPROCEEDINGS{svef,
author = {A. Detti and G. Bianchi and W. Kellerer and others},
title = {{SVEF}: an Open-Source Experimental Evaluation Framework},
booktitle = {In Proc. of {IEEE} {MediaWIN} 2009, Sousse, Tunisia},
year = {2009},
}
```

## Web Page and Contacts

 * http://svef.netgroup.uniroma2.it
 * Andrea Detti <andrea dot detti at uniroma2 dot it>
 * Claudio Pisa <claudio dot pisa at uniroma2 dot it>

