export PB_IP=$(/sbin/ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1) 
export IP=$PB_IP
export ANTIDOTE_NODENAME2=antidote@$IP
NODES=$ANTIDOTE_NODENAME2
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
sleep 4
echo "Connecting Controller to Switch with IP"
echo $PB_IP
for ip in "$@"
do
echo $ip
NODES+=" antidote@"$ip
done
./join_dcs_script.erl $NODES 
echo "Starting Table Creation"
cd ..
sudo python createtablescontroller.py
echo Starting Controller Initialization
sudo python -m ControllerDBCP.EventHandler
