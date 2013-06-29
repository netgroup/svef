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

#include "streamer.h"
#include <sys/time.h>

int 
isControlNALU(struct traceline *tl)
{
		if(tl->packettype != TRACELINE_PKT_SLICEDATA)
				return 0;

		if(tl->length == 8 || tl->length == 9 || tl->length == 10)
				return 1;
		else
				return 0;
}


void 
delay_loop_s(unsigned long nsec)
{
		struct timespec requested, remaining;

		requested.tv_sec  = 0;
		requested.tv_nsec = nsec;

		while (nanosleep(&requested, &remaining) == -1)
				if (errno == EINTR)
						requested = remaining;
				else 
				{
						fprintf(stderr, "Nanosleep error!\n");
						break;
				}
}

unsigned long
tdiff(struct timeval *end, struct timeval *start)
{ /* Returns time difference in nanoseconds between end and start */
       long ret;
	   ret = 1e9 * (end->tv_sec - start->tv_sec);
       ret += 1e3 * (end->tv_usec - start->tv_usec);
       return ret;
}

unsigned long
timeval2ulong(struct timeval *tv)
{
		/* time in millis */
		unsigned long ret;
		ret = 1e3 * tv->tv_sec;
		ret += 1e-3 * tv->tv_usec;
		return ret;
}


int
buildpacket(struct traceline *tl, struct ourpacket *nalutosend, FILE *videofile)
{ /* constructs a packet from a trace line */
		nalutosend->total_size = htons(tl->length + HEADER_SIZE);
		nalutosend->lid = tl->lid;
		nalutosend->tid = tl->tid;
		nalutosend->qid = tl->qid;

		if(tl->next == NULL)
				nalutosend->flags = STREAMER_LAST_PACKET;
		else
				nalutosend->flags = STREAMER_NOT_LAST_PACKET;
	
		switch(tl->packettype)
		{
				case TRACELINE_PKT_STREAMHEADER:
					nalutosend->flags |= STREAMER_NALU_TYPE_STREAMHEADER;
					break;
				case TRACELINE_PKT_PARAMETERSET:
					nalutosend->flags |= STREAMER_NALU_TYPE_PARAMETERSET;
					break;
				case TRACELINE_PKT_SLICEDATA:
					nalutosend->flags |= STREAMER_NALU_TYPE_SLICEDATA;
					break;
				default:
					nalutosend->flags |= STREAMER_NALU_TYPE_UNDEFINED;
		}
	
		if(tl->discardable == TRACELINE_YES)
				nalutosend->flags |= STREAMER_NALU_DISCARDABLE;
		else
				nalutosend->flags |= STREAMER_NALU_NOT_DISCARDABLE;
	
		if(tl->truncatable == TRACELINE_YES)
				nalutosend->flags |= STREAMER_NALU_TRUNCATABLE;
		else
				nalutosend->flags |= STREAMER_NALU_NOT_TRUNCATABLE;
	
		nalutosend->naluid = htonl(tl->startpos);
		nalutosend->frame_number = htons(tl->frameno);

		if(videofile != NULL)
		{
				/* real payload */
				fseek(videofile, tl->startpos, SEEK_SET);
				fread(&nalutosend->payload[0], 1, tl->length ,videofile); 
		}

	    //traceline_print_one(stderr, tl);
		return 0;
}

int 
main(int argc, char **argv)
{
		int sock, sb;
		struct sockaddr_in dest;
		struct hostent *h;
		struct rawtraceline *rt;
		struct traceline *tl;
		struct traceline *i;
		struct traceline *toprint1;
		struct traceline *toprint2;
		struct ourpacket nalutosend;
		struct ourpacket nextnalutosend;
		struct timeval tvstart, tvend, tvsent;
		unsigned long sleeping_interval, d; /* in nanoseconds */
		FILE *videofile = NULL;
		int payload_size, nalu1size, nalu2size, waitingseconds;
		float fps;
		// float tick;
		char tosend[MAX_PAYLOAD * 3];

		/* Check the command line
		 * 
		 *  ./streamer <tracefile> <fps> <destination_address> <port> 
		 */
		if(argc < 6) 
		{
				fprintf(stderr, "Usage: %s <tracefile> <fps> <destination_address> <port> <video file> [<seconds to wait before writing to standard output>]\n", argv[0]);
				exit(1);
		}

		fps = atof(argv[2]);

		sleeping_interval = 1e9 / fps; /* in nanoseconds */
		fprintf(stderr, "Sleeping interval: %lu nanoseconds\n", sleeping_interval);

		/*
		tick = 1.0 / (fps * STREAMER_RTP_CLOCK_FREQ); // not used but will be needed for RTP 
		fprintf(stderr, "Clock tick: %f\n", tick);
		*/

		if(argc >= 7)
				waitingseconds = atoi(argv[6]);
		else
				waitingseconds = STREAMER_SLEEP_AFTER_STREAM; 

		sock = socket(AF_INET, SOCK_DGRAM, 0);
		if(sock<0) exit(1);

		h = gethostbyname(argv[3]);
		if(!h) exit(2);

		memset(&dest, 0, sizeof(dest));

		dest.sin_family = AF_INET;
		memcpy(&dest.sin_addr.s_addr, h->h_addr, h->h_length);
		dest.sin_port = htons(atoi(argv[4]));

		/* Parse the file */
		traceline_parse_file(argv[1], &rt); 
		traceline_raws_to_normals(rt, &tl); 

		i = tl;
		if(i == NULL)
				return 0;
		
		/* skip the first lines */
		/*
		while(i->packettype == TRACELINE_PKT_UNDEFINED)
				i = i->next;
		*/

		if((videofile = fopen(argv[5], "r")) == NULL)
		{
			fprintf(stderr, "streamer.c %s\n", strerror(errno));
			exit(4);
		}

		gettimeofday(&tvstart, NULL);
		/* Iterating on the list of tracelines, pack and send them via UDP */
		while(i != NULL)
		{
			while(i->packettype != TRACELINE_PKT_SLICEDATA)
					i = i->next;
			
			toprint1 = NULL;
			toprint2 = NULL;
			buildpacket(i, &nalutosend, videofile);
			toprint1 = i;

			payload_size = ntohs(nalutosend.total_size);
			if (payload_size > MAX_PAYLOAD) 
			{
					fprintf(stderr, "Warning: packet too long: %d! Truncating...\n", ntohs(nalutosend.total_size)); 
					payload_size = MAX_PAYLOAD;
			}

			if(isControlNALU(i))
			{
					/* Take the next NALU and put it in the sending buffer */
					nalu1size = payload_size;
					nalutosend.flags |= STREAMER_NALU_TWONALUS;
					i = i->next;
					buildpacket(i, &nextnalutosend, videofile);
					toprint2 = i;
					nalu2size = ntohs(nextnalutosend.total_size);
					memcpy(&tosend[0], &nalutosend, nalu1size);
					memcpy(&tosend[nalu1size], &nextnalutosend, nalu2size); 
					payload_size = nalu1size + nalu2size; 
					if (payload_size > MAX_PAYLOAD) 
					{
							fprintf(stderr, "Warning: packet too long: %d! Truncating...\n", ntohs(nalutosend.total_size)); 
							payload_size = MAX_PAYLOAD;
					}
					gettimeofday(&tvend, NULL);
					d = tdiff(&tvend, &tvstart);
		    		delay_loop_s(sleeping_interval - d);
					gettimeofday(&tvstart, NULL);
 			} 
			else 
			{
					// tosend = nalutosend
					memcpy(&tosend, &nalutosend, payload_size);
			}

			gettimeofday(&tvsent, NULL);

			sb = sendto(
							sock, 
							&tosend, 
							(size_t) payload_size, 
							MSG_DONTWAIT, 
							(struct sockaddr *) &dest, 
							sizeof(dest)
					);

			if(sb==-1)
			{
					fprintf(stderr, "Error! %s\n", strerror(errno));
					fprintf(stderr, "payload_size = %d\n", payload_size);
					fprintf(stderr, "nalutosend total size: %d, naluid: %x\n", ntohs(nalutosend.total_size), ntohl(nalutosend.naluid));
					exit(-2);
			}
			
			toprint1->timestamp = timeval2ulong(&tvsent);
			//traceline_print_one(stdout, toprint1);
			if(toprint2 != NULL)
			{
				toprint2->timestamp = toprint1->timestamp;
				//traceline_print_one(stdout, toprint2);
			}

			i = i->next;
		}

		close(sock);
		sleep(waitingseconds);
		traceline_print(tl);
		fprintf(stderr, "tracefile printed\n");
		traceline_free(&tl);
		traceline_free_raw(&rt);
		if(videofile != NULL)
		{
				fclose(videofile);
		}

		return 0;
}

