#!/bin/bash

tc qdisc del dev eth1 parent root
tc qdisc del dev imq0 parent root
iptables -F -t nat
iptables -F -t mangle 
iptables -F 
