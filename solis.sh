#!/bin/bash
# ---------------------------------------------------------------
# A script to keep the SolisCloud2PVOutput.py script running.
# Change rick in this script below into your username
# Add to your crontab to run once a day, e.g. at 05:02 and at reboot
# 2 5 * * * ~/solis/solis.sh > /dev/null
# @reboot sleep 123 && ~/solis/solis.sh > /dev/null
# ---------------------------------------------------------------
script_name=$(basename -- "$0")
cd ~/solis

now=$(date)
if pidof -x "$script_name" -o $$ >/dev/null;then
   echo "$now: $script_name already running" >> solis.crontab.log 2>&1
   exit 1
fi
echo "ERROR: $now: $script_name NOT running" >> solis.crontab.log 2>&1
/usr/bin/python -u ~/solis/SolisCloud2PVOutput.py >> solis.log 2>&1 
