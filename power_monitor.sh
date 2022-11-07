#!/bin/bash

BAT=$(echo /sys/class/power_supply/BAT*)
BAT_STATUS="$BAT/status"
BAT_CAP="$BAT/capacity"
LOW_BAT_PERCENT=20
HIGH_CPU=60

AC_PROFILE="balanced"
BAT_PROFILE="power-saver"
PERFOMANCE_PROFILE="performance"

# #Service path
# # wait a while if needed
# [[ -z $STARTUP_WAIT ]] || sleep "$STARTUP_WAIT"

# start the monitor loop
prev=0

while true; do
    sleep 10
    CPU_IDLE=`top -b -n 1 | grep Cpu | awk '{print $8}'|cut -f 1 -d "."`
    CPU_USE=`expr 100 - $CPU_IDLE`
	# read the current state
	if [[ $(cat "$BAT_STATUS") == "Discharging" ]]; then
        profile=$BAT_PROFILE
        if [ $(cat "$BAT_CAP") -gt $LOW_BAT_PERCENT ] && [ $CPU_USE -gt $HIGH_CPU ]; then
            profile=$AC_PROFILE            
        fi
	else
        if [ $CPU_USE -gt $HIGH_CPU ]; then
            profile=$PERFOMANCE_PROFILE    
        else
            profile=$AC_PROFILE        
        fi
	fi
	# set the new profile
	if [[ $prev != "$profile" ]]; then
		echo setting power profile to $profile
		powerprofilesctl set $profile
	fi

	prev=$profile

	# # wait for the next power change event
	# inotifywait -qq "$BAT_STATUS" "$BAT_CAP"
done