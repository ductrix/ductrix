#!/bin/bash

#Usage
# <network_card_parms> <key_file_location> <key>
#

IFS=', ' read -r -a array <<< "$1"
shift
ename=$(/usr/bin/ls /sys/class/net/ | grep -v lo)

file="/etc/sysconfig/network-scripts/ifcfg-${ename}"

echo "NAME=${ename}" > ${file}
echo 'TYPE="ETHERNET"' >> ${file}
echo 'ONBOOT="yes"' >> ${file}


for element in "${array[@]}"
do
	echo "$element" >> ${file}
done

keyfile=${1}
shift
key=${1}
set -x
keydir=$(dirname $keyfile)
mkdir -p $keydir
chmod 700 $keydir 
echo "${key}" > ${keyfile}
chmod 600 $keyfile

/usr/bin/systemctl restart network

newip=$(ip addr show dev $ename | grep -o "inet [0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" | grep -o "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*")
echo "$newip" > /var/tmp/interface_ip.out
