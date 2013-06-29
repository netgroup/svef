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

INTERFACE=imq0
LIMIT=100
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


tc qdisc del dev $INTERFACE parent root

tc qdisc add dev $INTERFACE root handle 1: htb default 1
tc class add dev $INTERFACE parent 1: classid 1:1 htb rate ${C}kbit ceil ${C}kbit

tc qdisc add dev $INTERFACE parent 1:1 handle 2: pfifo limit $LIMIT 


