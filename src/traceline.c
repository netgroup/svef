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

#include "traceline.h"

/* parse a trace file and return a list of rawtraceline */
int 
traceline_parse_file(char *filename, struct rawtraceline **rawtracelinelist) 
{
		FILE *tracefile;
		int scannedpars = 1;
		struct rawtraceline *thisrt;
		struct rawtraceline *newrt;

		*rawtracelinelist = (struct rawtraceline *) malloc(sizeof(struct rawtraceline));
		thisrt = *rawtracelinelist;

		if((tracefile = fopen(filename, "r")) == NULL)
		{
				fprintf(stderr, "traceline.c: %s\n", strerror(errno));
				exit(10);
		}
		while(scannedpars != EOF)
		{
				scannedpars = fscanf(tracefile, " %as %as %as %as %as %as %as %as %as %as\n", 
							&thisrt->startpos,
							&thisrt->length,
							&thisrt->lid,
							&thisrt->tid,
							&thisrt->qid,
							&thisrt->packettype,
							&thisrt->discardable,
							&thisrt->truncatable,
							&thisrt->frameno,
							&thisrt->timestamp
							);
				assert(scannedpars == 10 || scannedpars == EOF);
				if(scannedpars != EOF)
				{
					newrt =  (struct rawtraceline *) malloc(sizeof(struct rawtraceline));

					/* double link */
					thisrt->next = newrt;
					newrt->prev = thisrt;

					thisrt = thisrt->next;
				}
				else
				{
					thisrt->prev->next = NULL;
					free(thisrt);
				}
		}

		fclose(tracefile);
		return 1;
}

void 
traceline_free_raw(struct rawtraceline **rt)
{
		struct rawtraceline *i = *rt;

		/* go to the end */
		if(i == NULL)
				return;

		while(i->next != NULL)
				i = i->next;

		/* free the mallocated structs and strings allocated with scanf's %as directive */
		while(i != *rt)
		{
				if(i->next != NULL)
					free(i->next);
				free(i->startpos);
				free(i->length);
				free(i->lid);
				free(i->tid);
				free(i->qid);
				free(i->packettype);
				free(i->discardable);
				free(i->truncatable);
				free(i->frameno);
				free(i->timestamp);
				i = i->prev;
		}
		free(i->startpos);
		free(i->length);
		free(i->lid);
		free(i->tid);
		free(i->qid);
		free(i->packettype);
		free(i->discardable);
		free(i->truncatable);
		free(i->frameno);
		free(i->timestamp);
}

void 
traceline_free(struct traceline **tl)
{
		struct traceline *i = *tl;

		/* go to the end */
		if(i == NULL)
				return;

		while(i->next != NULL)
				i = i->next;

		/* free the mallocated structs */
		while(i != *tl)
		{
				if(i->next != NULL)
					free(i->next);
				i = i->prev;
		}
}

void 
traceline_print_raw(struct rawtraceline *rt)
{
		struct rawtraceline *i = rt;

		while(i != NULL)
		{
				printf("[%s\t", i->startpos);
				printf("%s\t", i->length);
				printf("%s\t", i->lid);
				printf("%s\t", i->tid);
				printf("%s\t", i->qid);
				printf("%s\t", i->packettype);
				printf("%s\t", i->discardable);
				printf("%s\t", i->truncatable);
				printf("%s\t", i->frameno);
				printf("%s]\n", i->timestamp);
				i = i->next;
		}
}

/* convert a list of rawtraceline into a list of traceline */
int 
traceline_raws_to_normals(struct rawtraceline *inlist, struct traceline **outlist)
{
		struct rawtraceline *in;
		struct traceline *out;
		struct traceline *outnew;

		if(inlist == NULL)
				return -1;

		in = inlist;
		*outlist = (struct traceline *) malloc(sizeof(struct traceline));
		out = *outlist;

		while(in != NULL)
		{
				out->original = in;
				out->startpos = strtol(in->startpos, NULL, 16);
				out->length = atoi(in->length);
				out->lid = atoi(in->lid);
				out->tid = atoi(in->tid);
				out->qid = atoi(in->qid);

				if(!strcmp(in->packettype, "SliceData"))
				{
						out->packettype = TRACELINE_PKT_SLICEDATA;
				}
				else
				{
						if(!strcmp(in->packettype, "ParameterSet"))
										out->packettype = TRACELINE_PKT_PARAMETERSET;
						else
						{
							if(!strcmp(in->packettype, "StreamHeader"))
									out->packettype = TRACELINE_PKT_STREAMHEADER;
							else
									out->packettype = TRACELINE_PKT_UNDEFINED;
						}
				}

				if(!strcmp(in->discardable, "Yes"))
						out->discardable = TRACELINE_YES;
				else
						out->discardable = TRACELINE_NO;	

				if(!strcmp(in->truncatable, "Yes"))
						out->truncatable = TRACELINE_YES;
				else
						out->truncatable = TRACELINE_NO;
						
				out->timestamp = atol(in->timestamp);
				out->frameno = atol(in->frameno);

				outnew = (struct traceline *) malloc(sizeof(struct traceline));
				out->next = outnew;
				outnew->prev = out; 
				out = out->next;

				in = in->next;
		}
		out->prev->next= NULL;
		free(out);
		return 0;
}

void 
traceline_print(struct traceline *tl)
{ /* printf a list of traceline */
		struct traceline *i = tl;

		/*
		printf("Start-Pos.  Length  LId  TId  QId   Packet-Type  Discardable  Truncatable  Timestamp  Frame-number\n");
		printf("==========  ======  ===  ===  ===  ============  ===========  ===========  =========  ============\n");
		*/

		if(i==NULL)
				return;
		
		/* skip the first lines */
		while(i->packettype == TRACELINE_PKT_UNDEFINED)
				i = i->next;

		while(i != NULL)
		{
				traceline_print_one(stdout, i);
				i = i->next;
		}
}

void 
traceline_print_one(FILE *stream, struct traceline *tl)
{
		if(tl->startpos == 0)
				fprintf(stream, "0x00000000  ");
		else
				fprintf(stream, "%#010x  ", (unsigned int)tl->startpos);
		fprintf(stream, "%6d  ", tl->length);
		fprintf(stream, "%3d  ", tl->lid);
		fprintf(stream, "%3d  ", tl->tid);
		fprintf(stream, "%3d  ", tl->qid);
		switch(tl->packettype)
		{
				case TRACELINE_PKT_SLICEDATA:
						fprintf(stream, "   SliceData");
						break;
				case TRACELINE_PKT_STREAMHEADER:
						fprintf(stream, "StreamHeader");
						break;
				case TRACELINE_PKT_PARAMETERSET:
						fprintf(stream, "ParameterSet");
						break;
				default:
						//should never happen
						assert(0);
		}
		fprintf(stream, "  ");
		switch(tl->discardable)
		{
				case TRACELINE_YES:
						fprintf(stream, "       Yes ");
						break;
				default:
						fprintf(stream, "        No ");
		}
		fprintf(stream, "  ");
		switch(tl->truncatable)
		{
				case TRACELINE_YES:
						fprintf(stream, "      Yes");
						break;
				default:
						fprintf(stream, "       No");
		}
		if (tl->frameno >= 0)
			fprintf(stream, "  %8u", tl->frameno);
		else
			fprintf(stream, "  %8d", -1);
		fprintf(stream, "  %11lu", tl->timestamp);
		fprintf(stream, "\n");
		fflush(stream);
}

/*
int main()
{
		struct rawtraceline *rt;
		struct traceline *tl;
		traceline_parse_file("tracept.txt", &rt); 
		//traceline_print_raw(rt);
		traceline_raws_to_normals(rt, &tl); 
		traceline_print(tl);
		//printf("Freeing...\n");
		traceline_free_raw(&rt);
		traceline_free(&tl);
		return 0;
}
*/
