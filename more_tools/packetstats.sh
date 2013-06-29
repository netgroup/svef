#!/bin/bash

while /bin/true; do 
		cat /proc/net/dev | grep eth0 | cut -f 3 -d " " | cut -f 2 -d ":"; 
		sleep 1; 
done
