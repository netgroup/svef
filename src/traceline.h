/*
*  Copyright 2009 Claudio Pisa (claudio dot pisa at clauz dot net)
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

#ifndef TRACELINE_H
#define TRACELINE_H

#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>
#include <inttypes.h>
#include <errno.h>
#include <string.h>

/*
 *  SAMPLE TRACEFILE
  
Start-Pos.  Length  LId  TId  QId   Packet-Type  Discardable  Truncatable
==========  ======  ===  ===  ===  ============  ===========  ===========
0x00000000     238    0    0    0  StreamHeader          No          No
0x000000ee      13    0    0    0  ParameterSet          No          No
0x000000fb      16    0    0    0  ParameterSet          No          No
0x0000010b       8    0    0    0  ParameterSet          No          No
0x00000113       9    0    0    0  ParameterSet          No          No
0x0000011c       9    0    0    0  ParameterSet          No          No
0x00000125       9    0    0    0     SliceData          No          No
0x0000012e    3104    0    0    0     SliceData          No          No
0x00000d4e    7582    1    0    0     SliceData          No          No
0x00002aec       9    0    0    0     SliceData          No          No
0x00002af5    1931    0    0    0     SliceData          No          No
0x00003280    4690    1    0    0     SliceData          No          No
0x000044d2       9    0    1    0     SliceData         Yes          No
0x000044db    1048    0    1    0     SliceData         Yes          No
0x000048f3    1809    1    1    0     SliceData         Yes          No
0x00005004       9    0    2    0     SliceData         Yes          No

*/

#define TRACELINE_PKT_STREAMHEADER 0x0
#define TRACELINE_PKT_PARAMETERSET 0x1
#define TRACELINE_PKT_SLICEDATA 0x2
#define TRACELINE_PKT_UNDEFINED 0xff
#define TRACELINE_YES 0x1
#define TRACELINE_NO 0x0

typedef uint8_t traceline_onebyte_t;
typedef uint32_t traceline_fourbytes_t;

struct traceline  /* a formatted line of the tracefile */
{
		long int startpos;
		int length;
		traceline_onebyte_t lid;
		traceline_onebyte_t tid;
		traceline_onebyte_t qid;
		traceline_onebyte_t packettype;
		traceline_onebyte_t discardable;
		traceline_onebyte_t truncatable;
		unsigned frameno;
		unsigned long timestamp;
		struct traceline *next;
		struct traceline *prev;
		struct rawtraceline *original;
};

struct rawtraceline /* a raw (string) line of the tracefile */
{
		char *startpos;
		char *length;
		char *lid;
		char *tid;
		char *qid;
		char *packettype;
		char *discardable;
		char *truncatable;
		char *timestamp;
		char *frameno;
		struct rawtraceline *next;
		struct rawtraceline *prev;
};

/* convert a list of rawtraceline into a list of traceline */
int traceline_raws_to_normals(struct rawtraceline *inlist, struct traceline **outlist); 

/* parse a trace file and return a list of rawtraceline */
int traceline_parse_file(char *filename, struct rawtraceline **rawtracelinelist); 

/* printf a list of rawtraceline */
void traceline_print_raw(struct rawtraceline *rt);

/* destroy a list of rawtraceline */
void traceline_free_raw(struct rawtraceline **rt);

/* printf a list of traceline */
void traceline_print(struct traceline *tl);
void traceline_print_one(FILE *stream, struct traceline *tl);

/* destroy a list of traceline */
void traceline_free(struct traceline **tl);

#endif
