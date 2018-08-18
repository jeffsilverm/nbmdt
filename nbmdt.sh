#! /bin/bash
#
# This is a crude example of what a network diagnostic might look like
LOGFILE="network_`date +%F_%H-%M-%S`.txt"
## declare an array variable
declare -a NEIGHBORS4=("192.168.0.1" "192.168.0.5" "192.168.0.2" "192.168.0.3")
declare -a NEIGHBORS6=("fe80::1c33:6584:68e9:48eb%eno1", "fe80::106a:7a2f:61c2:e6b%eno1", \
	"fe80::29f5:52a5:53d5:fe1e%eno1", "fe80::4a5a:b6ff:fec4:1e67%eno1" )
declare -a FAVORITE_HOSTS_4=("google.com", "F5.COM", "amazon.com", "f5.ru", "f5.kr", "f5.il")
declare -a FAVORITE_HOSTS_6=("google.com", "F5.COM", "amazon.com", "f5.ru", "f5.kr", "f5.il")


echo "********${LOGFILE}********" > $LOGFILE
# this should update the neighbor tables for IPv4
nmap -sP 192.168.0.1-254 >> $LOGFILE
ip -4 -o link show >> $LOGFILE
ip -4 -o addr show >> $LOGFILE
ip -4 -o neigh show >> $LOGFILE
ip -4 -o route show >> $LOGFILE
for h in "${FAVORITE_HOSTS_4[@]}"; do
  echo $h >> $LOGFILE
  dig +short $h >> $LOGFILE
done 

ip -6 -o link show >> $LOGFILE
ip -6 -o addr show >> $LOGFILE
ip -6 -o neigh show >> $LOGFILE
ip -6 -o route show >> $LOGFILE
for h in "${FAVORITE_HOSTS_4[@]}"; do
  echo $h >> $LOGFILE
  dig -t aaaa +short $h >> $LOGFILE
done

echo "Results in $LOGFILE"
echo "********${LOGFILE}********" >> $LOGFILE

