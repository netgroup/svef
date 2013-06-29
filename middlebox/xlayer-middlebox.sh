#!/bin/bash
#
#  Copyright 2009 Claudio Pisa (claudio dot pisa at clauz dot net)
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

L=28 #Offset for LID in the header. 28 = 20 Bytes of  IP + 8 Bytes of UDP
T=29 #Offset for TID
Q=30 #Offset for QID
INTERFACE=imq0
LIMIT=35
C=$1  #HTB_bottleneck in kbit

if [ -z $C ]; then
	echo "Usage: $0 <bitrate in kbit/sec>";
	exit;
fi

modprobe imq
sleep 2
modprobe ip_conntrack
sleep 2

ifconfig imq0 up
iptables -F 
iptables -F -t nat
iptables -t mangle -A PREROUTING -i eth0 -j IMQ --todev 0

tc qdisc del dev $INTERFACE parent root

tc qdisc add dev $INTERFACE root handle 1: htb default 1
tc class add dev $INTERFACE parent 1: classid 1:1 htb rate ${C}kbit ceil ${C}kbit # burst 65K cburst 65K

tc qdisc add dev $INTERFACE parent 1:1 handle 2: prio bands 15

tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x00 0xFF at ${T} match u8 0x00 0xFF at ${Q} flowid 2:1 #TID 0 QID 0
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x01 0xFF at ${T} match u8 0x00 0xFF at ${Q} flowid 2:2 #TID 1 QID 0
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x02 0xFF at ${T} match u8 0x00 0xFF at ${Q} flowid 2:3 #TID 2 QID 0
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x03 0xFF at ${T} match u8 0x00 0xFF at ${Q} flowid 2:4 #TID 3 QID 0
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x04 0xFF at ${T} match u8 0x00 0xFF at ${Q} flowid 2:5 #TID 4 QID 0

tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x00 0xFF at ${T} match u8 0x01 0xFF at ${Q} flowid 2:6 #TID 0 QID 1
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x01 0xFF at ${T} match u8 0x01 0xFF at ${Q} flowid 2:7 #TID 1 QID 1
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x02 0xFF at ${T} match u8 0x01 0xFF at ${Q} flowid 2:8 #TID 2 QID 1
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x03 0xFF at ${T} match u8 0x01 0xFF at ${Q} flowid 2:9 #TID 3 QID 1
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x04 0xFF at ${T} match u8 0x01 0xFF at ${Q} flowid 2:a #TID 4 QID 1

tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x00 0xFF at ${T} match u8 0x02 0xFF at ${Q} flowid 2:b #TID 0 QID 2
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x01 0xFF at ${T} match u8 0x02 0xFF at ${Q} flowid 2:c #TID 1 QID 2
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x02 0xFF at ${T} match u8 0x02 0xFF at ${Q} flowid 2:d #TID 2 QID 2
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x03 0xFF at ${T} match u8 0x02 0xFF at ${Q} flowid 2:e #TID 3 QID 2
tc filter add dev $INTERFACE parent 2: protocol ip prio 1 u32 match u8 0x04 0xFF at ${T} match u8 0x02 0xFF at ${Q} flowid 2:f #TID 4 QID 2


tc qdisc add dev $INTERFACE parent 2:1 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:2 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:3 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:4 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:5 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:6 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:7 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:8 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:9 pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:a pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:b pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:c pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:d pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:e pfifo limit $LIMIT 
tc qdisc add dev $INTERFACE parent 2:f pfifo limit $LIMIT 

tc filter add dev $INTERFACE parent 2: protocol 0x0003 prio 2 u32 match u8 0x0 0x0 flowid 2:f #Default traffic

