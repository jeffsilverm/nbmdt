#! /bin/bash
#
# Automated network monitor.sh
#
# This script is a very crude but stil effective network monitor.  (see notes at end on how to make it better)
#
# Set to true if you want the script to use notify_send to send notifications
USE_notify_send=true
# How long to keep the notification visible in msec
END_EXPIRE_TIME=60000
PART_EXPIRE_TIME=10000
GOOD_EXPIRE_TIME=2000		# This is here only to reassure that the automated_network_monitor.sh script is running.
#
# How frequently to run (how long to sleep between runs) (10s = 10 seconds)
SLEEP_TIME=10s
#
#
# File to store the current state of the network
TEMP_STATE_FILE=/tmp/network_monitor.txt
#

handle_error() {
  COMMAND=$1
  ARGUMENTS=$2
  RETURN=$3
  echo "The arguments were $@"
  error_string="$(date -Is) PROBLEM: $COMMAND $ARGUMENTS $RETURN"
  if $USE_notify_send; then
    notify-send -u critical -t $PART_EXPIRE_TIME  "$error_string"
  fi
}

run_test() {
  COMMAND=$1
  shift
  ARGUMENTS=$@
  if $COMMAND $ARGUMENTS > /dev/null 2>>/dev/null; then
    ANY=true
    NONE=false
  else
    EVERY=false
    RESULT=$?
    handle_error $COMMAND $ARGUMENTS $RESULT
  fi
}

while true; do
  EVERY=true	# if any test fails, then make this false
  ANY=false	# if any test passes, then make this true
  NONE=true	# if any test passes, then make this false.
  run_test http http://google.com
  run_test http https://amazon.com
  run_test ssh -4 -T git@gitlab.com 
  run_test ssh -6 -T git@gitlab.com
  if $NONE; then
     notify-send -u critical -t $END_EXPIRE_TIME "$(date -Is) ***** CATASTROPHIC FAILURE ******"
  else
# If NONE is true, then neither EVERY nor ANY may be true.
    if $EVERY; then
# Note that if EVERY is true then ANY will also be true.  But ANY could be true, even if EVERY was false, but only if NONE was also false
      notify-send -u low -t $GOOD_EXPIRE_TIME "$(date -Is) ANM OK"
    else 
      notify-send -u normal -t $END_EXPIRE_TIME "$(date -Is) * There are some problems *"
    fi
  fi  
  sleep $SLEEP_TIME
done


# Some thoughts on how to make this better
# Re-write in python, perl or ruby - bash scripts are great for things that you just kinda bash (get it?) together
# but not very good for things you want in production.
# In python, there is the http and requests packages which do both http and https
# There are several ssh packages in PyPi
# There are also several packages that do desktop notification
# The idea is that forking processes all over the place is expensive.  Instead of forking processes, call subroutines.
#
#
# Test how well this works for failures:
# sudo ufw prepend reject out http comment "Use for inducing a failure in HTTP for testing ./automated_network_monitor.sh"
# sudo ufw delete reject out http 
# sudo ufw prepend reject out https comment "Use for inducing a failure in HTTPS for testing ./automated_network_monitor.sh"
# sudo ufw delete reject out http 
# sudo ufw prepend reject out ssh comment "Use for inducing a failure in SSH for testing ./automated_network_monitor.sh"
# sudo ufw delete reject out ssh
# sudo ufw prepend reject out 53 comment "Use for inducing a failure in DNS for testing ./automated_network_monitor.sh (this will break a lot of things"
# sudo ufw delete reject out 53 


