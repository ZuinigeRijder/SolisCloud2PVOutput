#!/bin/bash
# ---------------------------------------------------------------
#
# A script to keep the SolisCloud2PVOutput.py script running.
#
# ---------------------------------------------------------------
script_name=$(basename -- "$0")
cd /home/pi/solis

now=$(date)
if pidof -x "$script_name" -o $$ >/dev/null;then
   echo "$now: The script $script_name is already running" >> solis.crontab.log 2>&1
   exit 1
fi
echo "ERROR: $now: The script SolisCloud2PVOutput.py is not running" >> solis.crontab.log 2>&1
/usr/bin/python3 -u /home/pi/solis/SolisCloud2PVOutput.py >> solis.log 2>&1 
