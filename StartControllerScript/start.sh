#This variables are used to configure the IP of both Antidote and AQL nodes
#so that the controller is able to connect himself and the switches via script
export PB_IP=$(/sbin/ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1) 
export IP=$PB_IP
export ANTIDOTE_NODENAME2=antidote@$IP
NODES=$ANTIDOTE_NODENAME2
#Cleans Antidote logs and previous data, and start a new empty Antidote shell.
#The make compile and release step are not always necessary, but are important
#when the script is executed for the first time. 
#Screen is used to keep the shell active in the background
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
#Starts AQL. 
#Screen is used again to keep the shell active in the background.
echo "Starting AQL"
cd ..
cd AQL
screen -S AQL -d -m bash -c 'make shell;exec sh'
#The sleep is used to make sure that the AQL instance is
#up and running when the script that joins every component 
#is executed. This script requires as argument every node
#that we want to connect. Thats another reason why the machine's
#IP is necessary
sleep 4
echo "Connecting Controller to Switch with IP"
echo $PB_IP
for ip in "$@"
do
echo $ip
NODES+=" antidote@"$ip
done
cd ..
./join_dcs_script.erl $NODES 
#Create the tables necessary for the controller to function.
#Then ends by starting the controller processes
echo "Starting Table Creation"
sudo python createtablescontroller.py
echo "Starting Controller Initialization"
sudo python -m ControllerDBCP.EventHandler
