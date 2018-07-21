if [ $# -ne 1 ]
then
 echo "Invalid number of arguments. The number of arguments must be exactly 1"
 exit
fi
if [ $1 != "Switch" ] && [ $1  != "Controller" ]
then
 echo "Invalid name. Choose between Switch or Controller"
 exit
fi
sudo apt-get -y install build-essential && sudo apt-get -y update && sudo apt-get -y upgrade
wget erlang.org/download/otp_src_19.3.tar.gz
tar zfx otp_src_19.3.tar.gz
cd otp_src_19.3
sudo apt-get -y install libncurses-dev && sudo apt-get -y install default-jdk && sudo apt-get -y install g++
./configure
sudo make
sudo make install
cd ..
sudo apt-get -y update && sudo apt-get install -y screen && sudo apt-get install -y curl
git clone https://github.com/pedromslopes/antidote.git
cd antidote
if [ $1 = "Switch" ]; then
 git checkout 8b9d6735810110228347053ad01fc1505fa334f4
else
 git checkout 25aaa7a5c306ad5ba534c5a6281794922fe6c6a4
fi
git config --global url.https://github.com/.insteadOf git://github.com/
cd ..
git clone https://github.com/pedromslopes/AQL.git
cd AQL
if [ $1 = "Switch" ]; then
 git checkout new_features
else
 git checkout eb68cfa20c89187e2b26a0d47b99e46be0b978e9
fi
cd ..
sudo rm -rf otp_src_19.3.tar.gz
sudo rm -rf otp_src_19.3
sudo apt-get -y install python-pip
sudo pip install networkx
mv changetoinstall/antidote.erl antidote/src/
if [ $1 = "Switch" ]; then
 mv changetoinstall/triggers.erl antidote/src/
else
 mv changetoinstall2/triggers.erl antidote/src/
fi
mv changetoinstall/aqlparser.erl AQL/src/ 
mv changetoinstall/aql_http_handler.erl AQL/src/
rm -rf changetoinstall
rm -rf changetoinstall2
rm -rf OPXAQL
rm README.md
rm 80-dn-virt-intf.rules
if [ $1 = "Switch" ]; then
 sudo rm -rf ControllerDBCP
 rm createtablescontroller.py
 sudo rm -rf StartControllerScript
 mv StartSwitchScript/start.sh .
 rm -rf StartSwitchScript
 rm join_dcs_script.erl
else
 sudo rm -rf SwitchDBCP
 rm createtablesswitch.py
 sudo rm -rf StartSwitchScript
 mv StartControllerScript/start.sh .
 rm -rf StartControllerScript
 rm switchInterfaceStateChange.py
 chmod +x join_dcs_script.erl
fi
chmod +x start.sh
chmod +x stop.sh


