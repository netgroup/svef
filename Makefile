
SRCDIR=./src
PROGRAMS=receiver streamer 
REC_OBJS=$(SRCDIR)/traceline.o $(SRCDIR)/receiver.o
STR_OBJS=$(SRCDIR)/traceline.o $(SRCDIR)/streamer.o
#CFLAGS=-g
CFLAGS=-O2 -Wall 

all: $(PROGRAMS) 

receiver: $(REC_OBJS) 
	$(CC) $(CFLAGS) $(REC_OBJS) -o receiver

streamer: $(STR_OBJS)
	$(CC) $(CFLAGS) $(STR_OBJS) -o streamer 

receiver.o: $(SRCDIR)/receiver.c $(SRCDIR)/streamer.h
	$(CC) $(CFLAGS) -c $(SRCDIR)/receiver.c
	
streamer.o: $(SRCDIR)/streamer.c $(SRCDIR)/streamer.h
	$(CC) $(CFLAGS) -c $(SRCDIR)/streamer.c

traceline.o: $(SRCDIR)/traceline.c $(SRCDIR)/traceline.h
	$(CC) $(CFLAGS) -c $(SRCDIR)/traceline.c
	
clean:
	rm -f $(PROGRAMS) $(SRCDIR)/*.o


