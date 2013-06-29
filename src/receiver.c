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
#include "traceline.h"

struct traceline *tl;

int
decodepacket(struct traceline *newtl, struct ourpacket *pkt, FILE *outvideofile)
{
		newtl->length = ntohs(pkt->total_size) - HEADER_SIZE;
		newtl->lid = pkt->lid;
		newtl->tid = pkt->tid;
		newtl->qid = pkt->qid;
		newtl->startpos = ntohl(pkt->naluid);

		switch(pkt->flags & STREAMER_MASK_NALU_TYPE)
		{
				case STREAMER_NALU_TYPE_STREAMHEADER:
						newtl->packettype = TRACELINE_PKT_STREAMHEADER;
						break;
				case STREAMER_NALU_TYPE_PARAMETERSET:
						newtl->packettype = TRACELINE_PKT_PARAMETERSET;
						break;
				case STREAMER_NALU_TYPE_SLICEDATA:
						newtl->packettype = TRACELINE_PKT_SLICEDATA;
						break;
				default:
						newtl->packettype = TRACELINE_PKT_UNDEFINED;
		}

		if(!((pkt->flags & STREAMER_MASK_DISCARDABLE) ^ STREAMER_NALU_DISCARDABLE))
			newtl->discardable = TRACELINE_YES;
		else
			newtl->discardable = TRACELINE_NO;

		if(!((pkt->flags & STREAMER_MASK_TRUNCATABLE) ^ STREAMER_NALU_TRUNCATABLE))
			newtl->truncatable = TRACELINE_YES;
		else
			newtl->truncatable = TRACELINE_NO;

		newtl->frameno = ntohs(pkt->frame_number);

		//fprintf(stderr, "received: ");
		//traceline_print_one(stderr, newtl);

		/*
		traceline_print_one(stdout, newtl);
		fflush(stdout);
		*/

		// write on the H.264 file
		fwrite(pkt->payload, 1, newtl->length, outvideofile);
		fflush(outvideofile);

		return 0;
}

void
quitreceiver(int sig)
{
		fprintf(stderr, "Video time expired. Quitting...\n");
		traceline_free(&tl);
		exit(0);
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
main(int argc, char **argv)
{
		int sock, b;
		struct sockaddr_in sin, sin_other;
		socklen_t fromlen;
		char recvbuffer[MAX_PAYLOAD];
		struct ourpacket *recpacket; 
		struct ourpacket *secondpacket;
		struct traceline *newtl;
		struct timeval tv;
		int last = 0;
		FILE *outvideofile = NULL;
		char *filename;
		int videoduration;
		int alarmset = 0;

		/* Check the command line
		 * 
		 *  ./receiver <port> 
		 */
		if(argc < 4)
		{
				fprintf(stderr, "Usage: %s <listening port> <output H.264 file> <video duration in milliseconds>\n", argv[0]);
				exit(1);
		}

		signal(SIGALRM, quitreceiver);

		filename = argv[2];
		videoduration = atoi(argv[3]);

		fprintf(stderr, "Starting...\n");

		sock = socket(AF_INET, SOCK_DGRAM, 0);
		if(sock<0) exit(1);

		memset(&sin, 0, sizeof(sin));
		memset(&sin_other, 0, sizeof(sin_other));

		sin.sin_family = AF_INET;
		sin.sin_addr.s_addr = htonl(INADDR_ANY);
		sin.sin_port = htons(atoi(argv[1]));

		memset(&recvbuffer, 0, MAX_PAYLOAD);

		fprintf(stderr, "Binding...\n");
		b = bind(sock, (struct sockaddr *) &sin, sizeof(sin));
		if(b<0) exit(3);

		outvideofile = fopen(filename, "w");

		tl = (struct traceline *) malloc(sizeof(struct traceline));
		newtl = tl;
		while(!last)
		{
			recvfrom(sock, (void *) recvbuffer,  MAX_PAYLOAD, 0, (struct sockaddr *) &sin_other, &fromlen);
			gettimeofday(&tv, NULL);
			recpacket = (struct ourpacket *) recvbuffer;

			/* after the reception of the first packet, receive for a number of seconds equal to the duration of the video and then quit */
			if(alarmset == 0)
			{
					//alarm(videoduration);
					struct itimerval itv;
					itv.it_value.tv_sec = (long) (videoduration / 1000.0);
					itv.it_value.tv_usec = (videoduration % 1000) * 1000;
					setitimer(ITIMER_REAL, &itv, NULL);
					alarmset=1;
			}

			decodepacket(newtl, recpacket, outvideofile);
			newtl->timestamp = timeval2ulong(&tv);
			traceline_print_one(stdout, newtl);
			
			if(!((recpacket->flags & STREAMER_MASK_TWONALUS) ^ STREAMER_NALU_TWONALUS))
			{ /* Received packet contains two NAL units */
					newtl->next = (struct traceline *) malloc(sizeof(struct traceline));
					newtl->next->prev = newtl;
					newtl=newtl->next;
					secondpacket = (struct ourpacket *)(&recvbuffer[ntohs(recpacket->total_size)]);
					decodepacket(newtl, secondpacket, outvideofile);
					newtl->timestamp = timeval2ulong(&tv);
					traceline_print_one(stdout, newtl);					
					if(!((secondpacket->flags & STREAMER_MASK_LAST) ^ STREAMER_NOT_LAST_PACKET))
					{
							newtl->next = (struct traceline *) malloc(sizeof(struct traceline));
							newtl->next->prev = newtl;
							newtl=newtl->next;
					}
					else
					{
							fprintf(stderr, "Stream finished (2)\n");
							newtl->next = NULL;
							last = 1;
					}
			}
			else
			{
					if(!((recpacket->flags & STREAMER_MASK_LAST) ^ STREAMER_NOT_LAST_PACKET))
					{
							newtl->next = (struct traceline *) malloc(sizeof(struct traceline));
							newtl->next->prev = newtl;
							newtl=newtl->next;
					}
					else
					{
							fprintf(stderr, "Stream finished\n");
							newtl->next = NULL;
							last = 1;
					}
			}
			
		}

		close(sock);
		fclose(outvideofile);

//		traceline_print(tl);
		traceline_free(&tl);

		return 0;
}


