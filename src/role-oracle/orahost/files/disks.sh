#!/bin/bash
before_file=$(mktemp)
after_file=$(mktemp)
ls -l /dev/sd* | awk -F/ '{print $NF}' > $before_file
ls /sys/class/scsi_host/ | while read line ; do echo "- - -" > /sys/class/scsi_host/${line}/scan ; done 
sleep 10
ls -l /dev/sd* | awk -F/ '{print $NF}' > $after_file
echo $(grep -vf $before_file $after_file)
