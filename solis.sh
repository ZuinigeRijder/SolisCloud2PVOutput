#!/bin/bash
# ---------------------------------------------------------------
# A script to keep the soliscloud_to_pvoutput.py script running.
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
echo "WARNING: $now: $script_name NOT running" >> solis.crontab.log 2>&1
/usr/bin/python -u ~/solis/soliscloud_to_pvoutput.py >> solis.log 2>&1 
