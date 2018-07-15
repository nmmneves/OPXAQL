export PB_IP=$(/sbin/ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1) 
export IP=$PB_IP
export ANTIDOTE_NODENAME2=antidote@$IP
#export AQL_NAME=aql@$(/sbin/ifconfig |grep -A 1 eth0 | tail -l |cut -d : -f 2 | cut -d -f l))
echo "Starting Antidote"
cd antidote
rm -rf data.antidote@*
rm -rf data.nonode@*
rm -rf log
rm -rf log.nonode@*
rm -rf log.antidote@*
rm -rf _build/default/rel/
make compile > /dev/null 
make rel > /dev/null
screen -S antidote -d -m bash -c '_build/default/rel/antidote/bin/env console;exec sh' 
#_build/default/rel/antidote/bin/env console
echo "Starting AQL"
cd ..
cd AQL
screen -S AQL -d -m bash -c 'make shell;exec sh'
#make shell
sleep 3
declare -i i=1
for value in "$@"
do
echo "Setting Interface e101-00${i}-0 Up with IP = $value"
sudo ip addr add $value/24 dev e101-00${i}-0 
sudo ip link set dev e101-00${i}-0 up
i+=1
done
sleep 2
echo "Starting Table Creation"
cd ..
sudo python createtablesswitch.py
echo Starting Switch Initialization
sudo python -m SwitchDBCP.EventHandler
