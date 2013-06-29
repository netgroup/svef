/*
*  Copyright 2009 Claudio Pisa (claudio dot pisa at uniroma2 dot it)
*
*  This file is part of SVEF (SVC Streaming Evaluation Framework).
*
*  SVEF is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  SVEF is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with SVEF.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef STREAMER_H
#define STREAMER_H

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <inttypes.h>
#include <errno.h>
#include <time.h>
#include <signal.h>
#include <sys/time.h>

#include "traceline.h"

/* emulate RTP */
#define HEADER_SIZE 12 
#define MAX_PAYLOAD 65500

/* Constants used in the flags field (to be ORed) */
#define STREAMER_LAST_PACKET 0x80
#define STREAMER_NOT_LAST_PACKET 0x00
#define STREAMER_NALU_TYPE_STREAMHEADER 0x00
#define STREAMER_NALU_TYPE_PARAMETERSET 0x20
#define STREAMER_NALU_TYPE_SLICEDATA 0x40
#define STREAMER_NALU_TYPE_UNDEFINED 0x60
#define STREAMER_NALU_DISCARDABLE 0x10
#define STREAMER_NALU_NOT_DISCARDABLE 0x00
#define STREAMER_NALU_TRUNCATABLE 0x08
#define STREAMER_NALU_NOT_TRUNCATABLE 0x00
#define STREAMER_NALU_TWONALUS 0x04

#define STREAMER_MASK_LAST 0x80
#define STREAMER_MASK_NALU_TYPE 0x60
#define STREAMER_MASK_DISCARDABLE 0x10
#define STREAMER_MASK_TRUNCATABLE 0x08
#define STREAMER_MASK_TWONALUS 0x04

#define STREAMER_SLEEP_AFTER_STREAM 45

typedef uint8_t streamer_onebyte_t;
typedef uint16_t streamer_twobytes_t;
typedef uint32_t streamer_fourbytes_t;

/*      0               8              16              24              32
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
 */   

struct ourpacket
{
		streamer_onebyte_t lid;
		streamer_onebyte_t tid;
		streamer_onebyte_t qid;
		streamer_onebyte_t flags; /* 5 bits are used: last (1 bit), NALU type (2 bits), discardable (1 bit), truncatable (1 bit), two nalus (1 bit) */ 
		streamer_fourbytes_t naluid;
		streamer_twobytes_t total_size; /* in bytes */
		streamer_twobytes_t frame_number; /* departing from 0 */
		streamer_onebyte_t payload[MAX_PAYLOAD];
} __attribute__ ((packed));


extern FILE *outvideofile;

#endif

